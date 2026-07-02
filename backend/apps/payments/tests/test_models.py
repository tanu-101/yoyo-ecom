from __future__ import annotations

import pytest
from django.db import IntegrityError

from apps.payments.factories import PaymentEventFactory, PaymentFactory, RefundFactory
from apps.payments.models import Payment, PaymentEvent, Refund

pytestmark = pytest.mark.django_db


class TestPaymentModel:
    def test_create_payment(self):
        payment = PaymentFactory()
        assert Payment.objects.count() == 1
        assert str(payment).startswith("Payment")


class TestPaymentEventModel:
    def test_create_event(self):
        PaymentEventFactory()
        assert PaymentEvent.objects.count() == 1

    def test_unique_event_id(self):
        PaymentEventFactory(event_id="evt_001")
        with pytest.raises(IntegrityError):
            PaymentEventFactory(event_id="evt_001")


class TestRefundModel:
    def test_create_refund(self):
        refund = RefundFactory()
        assert Refund.objects.count() == 1
        assert refund.payment == refund.order.payments.first()
