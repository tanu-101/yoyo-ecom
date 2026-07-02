from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

import pytest

from apps.common.exceptions import BusinessRuleViolation
from apps.orders.constants import OrderStatus
from apps.orders.factories import OrderFactory
from apps.payments.constants import PaymentState, RefundState
from apps.payments.factories import PaymentFactory
from apps.payments.models import Payment, PaymentEvent
from apps.payments.services.refunds import process_refund
from apps.payments.services.stripe_payment_intents import (
    confirm_payment_failure,
    confirm_payment_success,
    create_payment_intent,
)
from apps.payments.services.stripe_webhooks import process_stripe_event

pytestmark = pytest.mark.django_db


class TestCreatePaymentIntent:
    def test_creates_intent_and_payment(self, customer_user):
        order = OrderFactory(
            customer=customer_user,
            status=OrderStatus.PENDING_PAYMENT,
            total_amount=Decimal("150.00"),
        )
        fake_intent = {
            "id": "pi_test_123",
            "client_secret": "pi_test_123_secret_xyz",
            "amount": 15000,
            "currency": "usd",
        }

        with patch(
            "apps.payments.services.stripe_payment_intents.stripe.PaymentIntent.create",
            return_value=fake_intent,
        ):
            result = create_payment_intent(order=order, customer=customer_user)

        assert result["client_secret"] == "pi_test_123_secret_xyz"
        payment = Payment.objects.get(id=result["payment"])
        assert payment.provider_payment_intent_id == "pi_test_123"
        assert payment.amount == Decimal("150.00")
        assert payment.status == PaymentState.PENDING
        assert payment.metadata["client_secret"] == "pi_test_123_secret_xyz"

    def test_returns_existing_pending_intent(self, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.PENDING_PAYMENT)
        payment = PaymentFactory(
            order=order,
            status=PaymentState.PENDING,
            provider_payment_intent_id="pi_existing",
            metadata={"client_secret": "existing_secret"},
        )

        result = create_payment_intent(order=order, customer=customer_user)

        assert result["payment"] == payment.id
        assert result["client_secret"] == "existing_secret"
        assert Payment.objects.count() == 1

    def test_raises_if_not_owner(self, customer_user, admin_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.PENDING_PAYMENT)
        with pytest.raises(BusinessRuleViolation, match="does not belong"):
            create_payment_intent(order=order, customer=admin_user)

    def test_raises_if_not_pending_payment(self, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.PLACED)
        with pytest.raises(BusinessRuleViolation, match="not pending payment"):
            create_payment_intent(order=order, customer=customer_user)


class TestConfirmPaymentSuccess:
    def test_marks_payment_and_order_as_paid(self):
        payment = PaymentFactory(status=PaymentState.PENDING)
        result = confirm_payment_success(payment=payment, provider_payment_intent_id="pi_confirmed")

        result.refresh_from_db()
        assert result.status == PaymentState.SUCCEEDED
        assert result.provider_payment_intent_id == "pi_confirmed"
        assert result.processed_at is not None

        order = result.order
        order.refresh_from_db()
        assert order.payment_status == "paid"
        assert order.paid_at is not None


class TestConfirmPaymentFailure:
    def test_marks_payment_as_failed(self):
        payment = PaymentFactory(status=PaymentState.PENDING)
        result = confirm_payment_failure(payment=payment, failure_reason="Card declined")

        result.refresh_from_db()
        assert result.status == PaymentState.FAILED
        assert result.failure_reason == "Card declined"


class TestProcessRefund:
    def test_create_stripe_refund_and_local_record(self, customer_user):
        payment = PaymentFactory(
            status=PaymentState.SUCCEEDED,
            provider_payment_intent_id="pi_refund_test",
            amount=Decimal("200.00"),
        )
        fake_stripe_refund = {
            "id": "re_stripe_123",
            "payment_intent": "pi_refund_test",
            "amount": 5000,
            "currency": "usd",
            "status": "succeeded",
        }

        with patch(
            "apps.payments.services.refunds.stripe.Refund.create",
            return_value=fake_stripe_refund,
        ):
            refund = process_refund(
                payment=payment,
                amount=Decimal("50.00"),
                reason="Customer requested",
                created_by=customer_user,
            )

        assert refund.status == RefundState.SUCCEEDED
        assert refund.provider_refund_id == "re_stripe_123"
        assert refund.amount == Decimal("50.00")
        assert refund.created_by == customer_user

        payment.order.refresh_from_db()
        assert payment.order.payment_status == "partially_refunded"

    def test_raises_on_unsuccessful_payment(self):
        payment = PaymentFactory(status=PaymentState.FAILED)
        with pytest.raises(BusinessRuleViolation, match="not successful"):
            process_refund(payment=payment, amount=Decimal("10.00"))

    def test_raises_if_amount_exceeds_remaining(self):
        payment = PaymentFactory(
            status=PaymentState.SUCCEEDED,
            amount=Decimal("100.00"),
        )
        with pytest.raises(BusinessRuleViolation, match="exceeds remaining"):
            process_refund(payment=payment, amount=Decimal("200.00"))


class TestProcessStripeEvent:
    def test_handles_payment_intent_succeeded(self):
        payment = PaymentFactory(
            status=PaymentState.PENDING,
            provider_payment_intent_id="pi_success_1",
        )
        payload = {
            "id": "evt_success_1",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_success_1",
                    "charges": {
                        "data": [{"id": "ch_123"}],
                    },
                }
            },
        }

        result = process_stripe_event(
            event_id="evt_success_1",
            event_type="payment_intent.succeeded",
            payload=payload,
        )

        assert result["status"] == "processed"
        payment.refresh_from_db()
        assert payment.status == PaymentState.SUCCEEDED
        assert payment.provider_charge_id == "ch_123"

    def test_handles_payment_intent_failed(self):
        payment = PaymentFactory(
            status=PaymentState.PENDING,
            provider_payment_intent_id="pi_fail_1",
        )
        payload = {
            "id": "evt_fail_1",
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_fail_1",
                    "last_payment_error": {"message": "Card declined"},
                }
            },
        }

        result = process_stripe_event(
            event_id="evt_fail_1",
            event_type="payment_intent.payment_failed",
            payload=payload,
        )

        assert result["status"] == "processed"
        payment.refresh_from_db()
        assert payment.status == PaymentState.FAILED
        assert payment.failure_reason == "Card declined"

    def test_handles_charge_refunded(self):
        payment = PaymentFactory(
            status=PaymentState.SUCCEEDED,
            provider_charge_id="ch_refund_1",
        )
        payload = {
            "id": "evt_refund_1",
            "type": "charge.refunded",
            "data": {
                "object": {
                    "id": "ch_refund_1",
                    "amount_refunded": 5000,
                }
            },
        }

        result = process_stripe_event(
            event_id="evt_refund_1",
            event_type="charge.refunded",
            payload=payload,
        )

        assert result["status"] == "processed"
        assert result["payment_id"] == str(payment.id)

    def test_deduplicates_already_processed_event(self):
        payload = {
            "id": "evt_dup",
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_dup"}},
        }
        process_stripe_event(
            event_id="evt_dup",
            event_type="payment_intent.succeeded",
            payload=payload,
        )

        result2 = process_stripe_event(
            event_id="evt_dup",
            event_type="payment_intent.succeeded",
            payload=payload,
        )

        assert result2["status"] == "duplicate"

    def test_no_payment_found_logs_error(self):
        payload = {
            "id": "evt_none",
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_nonexistent"}},
        }

        result = process_stripe_event(
            event_id="evt_none",
            event_type="payment_intent.succeeded",
            payload=payload,
        )

        assert result["status"] == "processed"
        event = PaymentEvent.objects.get(event_id="evt_none")
        assert "No payment found" in event.processing_error

    def test_handles_exception_gracefully(self):
        payload = {
            "id": "evt_err",
            "type": "payment_intent.succeeded",
            "data": {"object": {}},
        }

        result = process_stripe_event(
            event_id="evt_err",
            event_type="payment_intent.succeeded",
            payload=payload,
        )

        assert result["status"] == "processed"

    def test_reprocess_old_event(self):
        event = PaymentEvent.objects.create(
            provider="stripe",
            event_id="evt_repro",
            event_type="payment_intent.succeeded",
            payload={},
            processed_at=None,
        )

        payload = {
            "id": "evt_repro",
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_repro"}},
        }
        result = process_stripe_event(
            event_id="evt_repro",
            event_type="payment_intent.succeeded",
            payload=payload,
        )

        assert result["status"] == "reprocessed"
        event.refresh_from_db()
        assert event.processed_at is not None
