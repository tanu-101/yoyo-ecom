from __future__ import annotations

import factory

from apps.orders.factories import OrderFactory
from apps.shipping.constants import TrackingStatus
from apps.shipping.models import OrderTracking, ShippingMethod


class ShippingMethodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShippingMethod

    name = factory.Sequence(lambda n: f"Shipping Method {n}")
    code = factory.Sequence(lambda n: f"ship-{n}")
    base_price = 10.00
    price_per_kg = 2.00
    is_active = True


class OrderTrackingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderTracking

    order = factory.SubFactory(OrderFactory)
    carrier = "FedEx"
    tracking_number = factory.Sequence(lambda n: f"TRK{n:08d}")
    status = TrackingStatus.PROCESSING
