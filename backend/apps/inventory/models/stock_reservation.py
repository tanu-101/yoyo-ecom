from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import TimeStampedModel
from apps.inventory.constants import StockReservationStatus


class StockReservation(TimeStampedModel):
    variant: models.ForeignKey = models.ForeignKey(
        "catalog.Variant",
        on_delete=models.CASCADE,
        related_name="stock_reservations",
    )
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stock_reservations",
    )
    order: models.ForeignKey = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_reservations",
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField()
    status: models.CharField = models.CharField(
        max_length=20,
        choices=StockReservationStatus.choices,
        default=StockReservationStatus.ACTIVE,
    )
    expires_at: models.DateTimeField = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["variant"]),
            models.Index(fields=["user"]),
            models.Index(fields=["order"]),
            models.Index(fields=["status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return f"Reservation for {self.variant.sku} by {self.user.email}"
