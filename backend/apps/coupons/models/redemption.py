from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import UUIDModel


class CouponRedemption(UUIDModel):
    coupon: models.ForeignKey = models.ForeignKey(
        "coupons.Coupon",
        on_delete=models.CASCADE,
        related_name="redemptions",
    )
    customer: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coupon_redemptions",
    )
    order: models.ForeignKey = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="coupon_redemptions",
    )
    discount_amount: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["coupon", "order"], name="unique_coupon_order"),
        ]
        indexes = [
            models.Index(fields=["coupon"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["coupon", "customer"]),
        ]

    def __str__(self) -> str:
        return f"{self.coupon.code} - {self.customer.email}"
