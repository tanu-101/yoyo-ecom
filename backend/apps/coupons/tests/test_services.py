from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.common.exceptions import BusinessRuleViolation
from apps.coupons.factories import CouponFactory
from apps.coupons.models import CouponRedemption
from apps.coupons.services.validation import apply_coupon, calculate_discount, validate_coupon
from apps.orders.factories import OrderFactory

pytestmark = pytest.mark.django_db


class TestValidateCoupon:
    def test_valid_coupon(self, customer_user):
        coupon = CouponFactory()

        result = validate_coupon(
            code=coupon.code, customer=customer_user, order_total=Decimal("100.00")
        )

        assert result == coupon

    def test_raises_on_expired_coupon(self, customer_user):
        coupon = CouponFactory(valid_until=timezone.now() - timedelta(days=1))

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_coupon(code=coupon.code, customer=customer_user, order_total=Decimal("100.00"))

        assert exc.value.code == "coupon_expired"

    def test_raises_on_not_yet_valid(self, customer_user):
        coupon = CouponFactory(valid_from=timezone.now() + timedelta(days=1))

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_coupon(code=coupon.code, customer=customer_user, order_total=Decimal("100.00"))

        assert exc.value.code == "coupon_invalid"

    def test_raises_on_inactive_coupon(self, customer_user):
        coupon = CouponFactory(is_active=False)

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_coupon(code=coupon.code, customer=customer_user, order_total=Decimal("100.00"))

        assert exc.value.code == "coupon_invalid"

    def test_raises_on_min_order_value_not_met(self, customer_user):
        coupon = CouponFactory(min_order_value=100.00)

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_coupon(code=coupon.code, customer=customer_user, order_total=Decimal("50.00"))

        assert exc.value.code == "coupon_invalid"

    def test_raises_on_per_customer_limit_exceeded(self, customer_user):
        coupon = CouponFactory(per_customer_limit=1)
        prior_order = OrderFactory(customer=customer_user)
        CouponRedemption.objects.create(
            coupon=coupon,
            customer=customer_user,
            order=prior_order,
            discount_amount=Decimal("5.00"),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_coupon(code=coupon.code, customer=customer_user, order_total=Decimal("100.00"))

        assert exc.value.code == "coupon_usage_limit_reached"

    def test_raises_on_usage_limit_reached(self, customer_user):
        coupon = CouponFactory(max_usage_count=1, usage_count=1)

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_coupon(code=coupon.code, customer=customer_user, order_total=Decimal("100.00"))

        assert exc.value.code == "coupon_usage_limit_reached"


class TestCalculateDiscount:
    def test_percentage_discount(self):
        coupon = CouponFactory(discount_type="percentage", discount_value=Decimal("10.00"))
        discount = calculate_discount(coupon=coupon, order_total=Decimal("200.00"))
        assert discount == Decimal("20.00")

    def test_fixed_amount_discount(self):
        coupon = CouponFactory(discount_type="fixed_amount", discount_value=25.00)
        discount = calculate_discount(coupon=coupon, order_total=Decimal("200.00"))
        assert discount == Decimal("25.00")

    def test_fixed_amount_capped_at_order_total(self):
        coupon = CouponFactory(discount_type="fixed_amount", discount_value=50.00)
        discount = calculate_discount(coupon=coupon, order_total=Decimal("30.00"))
        assert discount == Decimal("30.00")

    def test_percentage_with_max_discount_cap(self):
        coupon = CouponFactory(
            discount_type="percentage",
            discount_value=Decimal("25.00"),
            max_discount_amount=Decimal("30.00"),
        )
        discount = calculate_discount(coupon=coupon, order_total=Decimal("200.00"))
        # 25% of 200 = 50, capped at 30
        assert discount == Decimal("30.00")

    def test_percentage_below_max_cap(self):
        coupon = CouponFactory(
            discount_type="percentage",
            discount_value=Decimal("10.00"),
            max_discount_amount=Decimal("50.00"),
        )
        discount = calculate_discount(coupon=coupon, order_total=Decimal("200.00"))
        # 10% of 200 = 20, below cap of 50
        assert discount == Decimal("20.00")


class TestApplyCoupon:
    def test_applies_coupon_and_creates_redemption(self, customer_user):
        coupon = CouponFactory(discount_type="percentage", discount_value=10.00)
        order = OrderFactory(customer=customer_user, total_amount=Decimal("200.00"))

        result_coupon, discount = apply_coupon(
            code=coupon.code,
            customer=customer_user,
            order=order,
            order_total=Decimal("200.00"),
        )

        assert result_coupon == coupon
        assert discount == Decimal("20.00")

        assert (
            CouponRedemption.objects.filter(
                coupon=coupon, customer=customer_user, order=order
            ).count()
            == 1
        )

        coupon.refresh_from_db()
        assert coupon.usage_count == 1

    def test_raises_on_invalid_coupon(self, customer_user):
        order = OrderFactory(customer=customer_user)

        with pytest.raises(BusinessRuleViolation):
            apply_coupon(
                code="INVALID", customer=customer_user, order=order, order_total=Decimal("100.00")
            )
