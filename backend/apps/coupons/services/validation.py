from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.accounts.models import User
from apps.common.exceptions import BusinessRuleViolation
from apps.coupons.models import Coupon, CouponRedemption
from apps.coupons.selectors.coupons import get_coupon_by_code
from apps.orders.models import Order


def validate_coupon(*, code: str, customer: User, order_total: Decimal) -> Coupon:
    coupon = get_coupon_by_code(code=code)
    if not coupon:
        raise BusinessRuleViolation("Invalid coupon code.", code="coupon_invalid")

    now = timezone.now()
    if coupon.valid_from > now:
        raise BusinessRuleViolation("Coupon is not yet valid.", code="coupon_invalid")

    if coupon.valid_until and coupon.valid_until < now:
        raise BusinessRuleViolation("Coupon has expired.", code="coupon_expired")

    if not coupon.is_active or coupon.deleted_at is not None:
        raise BusinessRuleViolation("Coupon is no longer active.", code="coupon_invalid")

    if coupon.max_usage_count is not None and coupon.usage_count >= coupon.max_usage_count:
        raise BusinessRuleViolation(
            "Coupon usage limit reached.", code="coupon_usage_limit_reached"
        )

    if order_total < coupon.min_order_value:
        raise BusinessRuleViolation(
            f"Minimum order value of {coupon.min_order_value} required.",
            code="coupon_invalid",
        )

    customer_usage = CouponRedemption.objects.filter(
        coupon=coupon,
        customer=customer,
    ).count()
    if customer_usage >= coupon.per_customer_limit:
        raise BusinessRuleViolation(
            "Coupon per-customer limit reached.",
            code="coupon_usage_limit_reached",
        )

    return coupon


def calculate_discount(*, coupon: Coupon, order_total: Decimal) -> Decimal:
    if coupon.discount_type == "percentage":
        discount = order_total * (coupon.discount_value / Decimal("100"))
        if coupon.max_discount_amount is not None:
            discount = min(discount, coupon.max_discount_amount)
    else:
        discount = min(coupon.discount_value, order_total)

    return discount


@transaction.atomic
def apply_coupon(
    *,
    code: str,
    customer: User,
    order: Order,
    order_total: Decimal,
) -> tuple[Coupon, Decimal]:
    coupon = validate_coupon(code=code, customer=customer, order_total=order_total)
    discount = calculate_discount(coupon=coupon, order_total=order_total)

    CouponRedemption.objects.create(
        coupon=coupon,
        customer=customer,
        order=order,
        discount_amount=discount,
    )

    Coupon.objects.filter(id=coupon.id).update(usage_count=F("usage_count") + 1)

    return coupon, discount
