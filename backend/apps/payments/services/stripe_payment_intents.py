from __future__ import annotations

from decimal import Decimal

import stripe
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.common.exceptions import BusinessRuleViolation
from apps.orders.constants import OrderStatus
from apps.orders.models import Order
from apps.payments.constants import PaymentProvider, PaymentState
from apps.payments.models import Payment


def _cents_from_decimal(amount: Decimal) -> int:
    return int(amount * 100)


@transaction.atomic
def create_payment_intent(*, order: Order, customer: User) -> dict:
    if order.customer_id != customer.id:
        raise BusinessRuleViolation(
            "Order does not belong to this customer.",
            code="permission_denied",
        )

    if order.status != OrderStatus.PENDING_PAYMENT:
        raise BusinessRuleViolation("Order is not pending payment.", code="invalid_order_status")

    existing = Payment.objects.filter(order=order, status=PaymentState.PENDING).first()
    if existing:
        return {
            "payment": existing.id,
            "client_secret": (
                existing.metadata.get("client_secret", "") if existing.metadata else ""
            ),
        }

    stripe_intent = stripe.PaymentIntent.create(
        amount=_cents_from_decimal(order.total_amount),
        currency="usd",
        metadata={"order_id": str(order.id), "customer_id": str(customer.id)},
        description=f"Order {order.order_number}",
    )

    payment = Payment.objects.create(
        order=order,
        provider=PaymentProvider.STRIPE,
        provider_payment_intent_id=stripe_intent["id"],
        amount=order.total_amount,
        currency="USD",
        status=PaymentState.PENDING,
        metadata={"client_secret": stripe_intent["client_secret"]},
    )

    return {
        "payment": payment.id,
        "client_secret": stripe_intent["client_secret"],
    }


def confirm_payment_success(*, payment: Payment, provider_payment_intent_id: str) -> Payment:
    payment.status = PaymentState.SUCCEEDED
    payment.provider_payment_intent_id = provider_payment_intent_id
    payment.processed_at = timezone.now()
    payment.save(
        update_fields=["status", "provider_payment_intent_id", "processed_at", "updated_at"]
    )

    order = payment.order
    order.payment_status = "paid"
    order.paid_at = timezone.now()
    order.save(update_fields=["payment_status", "paid_at", "updated_at"])

    return payment


def confirm_payment_failure(*, payment: Payment, failure_reason: str = "") -> Payment:
    payment.status = PaymentState.FAILED
    payment.failure_reason = failure_reason
    payment.save(update_fields=["status", "failure_reason", "updated_at"])
    return payment
