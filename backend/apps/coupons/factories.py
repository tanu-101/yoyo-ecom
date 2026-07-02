from __future__ import annotations

from datetime import timedelta

import factory
from django.utils import timezone

from apps.coupons.models import Coupon


class CouponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Coupon

    code = factory.Sequence(lambda n: f"PROMO{n:04d}")
    discount_type = "percentage"
    discount_value = 10.00
    min_order_value = 50.00
    per_customer_limit = 1
    valid_from = factory.LazyFunction(timezone.now)
    valid_until = factory.LazyFunction(lambda: timezone.now() + timedelta(days=30))
    is_active = True
