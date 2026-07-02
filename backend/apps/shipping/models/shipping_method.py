from __future__ import annotations

from django.db import models

from apps.common.models.base import TimeStampedModel


class ShippingMethod(TimeStampedModel):
    name: models.CharField = models.CharField(max_length=255)
    code: models.CharField = models.CharField(max_length=100, unique=True)
    description: models.TextField = models.TextField(blank=True, default="")
    base_price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    estimated_min_days: models.PositiveIntegerField = models.PositiveIntegerField(default=1)
    estimated_max_days: models.PositiveIntegerField = models.PositiveIntegerField(default=7)
    is_active: models.BooleanField = models.BooleanField(default=True)

    class Meta:
        ordering = ["base_price"]

    def __str__(self) -> str:
        return self.name
