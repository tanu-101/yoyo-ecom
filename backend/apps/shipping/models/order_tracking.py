from __future__ import annotations

from django.db import models

from apps.common.models.base import TimeStampedModel
from apps.shipping.constants import TrackingStatus


class OrderTracking(TimeStampedModel):
    order: models.OneToOneField = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="tracking",
    )
    carrier: models.CharField = models.CharField(max_length=255)
    tracking_number: models.CharField = models.CharField(max_length=255, unique=True)
    tracking_url: models.URLField = models.URLField(blank=True, default="")
    status: models.CharField = models.CharField(
        max_length=30,
        choices=TrackingStatus.choices,
        default=TrackingStatus.PROCESSING,
    )
    estimated_delivery: models.DateField = models.DateField(null=True, blank=True)
    last_update: models.DateTimeField = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["tracking_number"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.carrier}: {self.tracking_number}"
