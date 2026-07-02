from __future__ import annotations

import pytest

from apps.coupons.factories import CouponFactory
from apps.coupons.models import Coupon

pytestmark = pytest.mark.django_db


class TestCouponModel:
    def test_create_coupon(self):
        coupon = CouponFactory()
        assert Coupon.objects.count() == 1
        assert str(coupon) == coupon.code
