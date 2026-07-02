from __future__ import annotations

import factory

from apps.orders.factories import OrderFactory
from apps.payments.constants import PaymentProvider, PaymentState, RefundState
from apps.payments.models import Payment, PaymentEvent, Refund


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    order = factory.SubFactory(OrderFactory)
    provider = PaymentProvider.STRIPE
    provider_payment_intent_id = factory.Sequence(lambda n: f"pi_{n:010d}")
    amount = 115.00
    currency = "USD"
    status = PaymentState.PENDING


class PaymentEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PaymentEvent

    provider = PaymentProvider.STRIPE
    event_id = factory.Sequence(lambda n: f"evt_{n:010d}")
    event_type = "payment_intent.succeeded"
    payload = {"data": {"object": {"id": "pi_test", "amount": 11500}}}


class RefundFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Refund

    payment = factory.SubFactory(PaymentFactory)
    order = factory.SelfAttribute("payment.order")
    amount = 50.00
    status = RefundState.SUCCEEDED
