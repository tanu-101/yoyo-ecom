from __future__ import annotations

from django.db import models

from apps.common.models.base import SoftDeleteModel


class DiscountType(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage"
    FIXED_AMOUNT = "fixed_amount", "Fixed amount"


class Coupon(SoftDeleteModel):
    code: models.CharField = models.CharField(max_length=50, unique=True)
    description: models.TextField = models.TextField(blank=True, default="")
    discount_type: models.CharField = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    max_discount_amount: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    max_usage_count: models.PositiveIntegerField = models.PositiveIntegerField(
        null=True, blank=True
    )
    usage_count: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    per_customer_limit: models.PositiveIntegerField = models.PositiveIntegerField(default=1)
    valid_from: models.DateTimeField = models.DateTimeField()
    valid_until: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    is_active: models.BooleanField = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["valid_from"]),
            models.Index(fields=["valid_until"]),
        ]

    def __str__(self) -> str:
        return self.code
