from __future__ import annotations

import factory

from apps.accounts.factories import CustomerUserFactory
from apps.orders.factories import OrderFactory, OrderItemFactory
from apps.returns.models import ReturnImage, ReturnItem, ReturnRequest


class ReturnRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReturnRequest

    return_number = factory.Sequence(lambda n: f"RET-2026-{n + 1:06d}")
    order = factory.SubFactory(OrderFactory)
    customer = factory.SubFactory(CustomerUserFactory)
    reason = "defective"
    status = "pending_review"


class ReturnItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReturnItem

    return_request = factory.SubFactory(ReturnRequestFactory)
    order_item = factory.SubFactory(OrderItemFactory)
    quantity = 1
    reason = "defective"


class ReturnImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReturnImage

    return_request = factory.SubFactory(ReturnRequestFactory)
    image = "https://example.com/image.jpg"
