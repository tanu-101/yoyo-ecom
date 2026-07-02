from __future__ import annotations

from django.db import models

from apps.common.models.base import TimeStampedModel


class OrderShippingAddress(TimeStampedModel):
    order: models.OneToOneField = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="shipping_address",
    )
    full_name: models.CharField = models.CharField(max_length=255)
    phone: models.CharField = models.CharField(max_length=50)
    line1: models.CharField = models.CharField(max_length=255)
    line2: models.CharField = models.CharField(max_length=255, blank=True, default="")
    city: models.CharField = models.CharField(max_length=255)
    state: models.CharField = models.CharField(max_length=255, blank=True, default="")
    postal_code: models.CharField = models.CharField(max_length=50)
    country: models.CharField = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.full_name}, {self.city}"
