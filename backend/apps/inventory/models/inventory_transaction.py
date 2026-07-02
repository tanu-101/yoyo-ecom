from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import UUIDModel
from apps.inventory.constants import InventoryTransactionType


class InventoryTransaction(UUIDModel):
    variant: models.ForeignKey = models.ForeignKey(
        "catalog.Variant",
        on_delete=models.CASCADE,
        related_name="inventory_transactions",
    )
    transaction_type: models.CharField = models.CharField(
        max_length=50,
        choices=InventoryTransactionType.choices,
    )
    quantity_changed: models.IntegerField = models.IntegerField()
    stock_before: models.IntegerField = models.IntegerField()
    stock_after: models.IntegerField = models.IntegerField()
    reference_type: models.CharField = models.CharField(max_length=100, blank=True, default="")
    reference_id: models.UUIDField = models.UUIDField(null=True, blank=True)
    notes: models.TextField = models.TextField(blank=True, default="")
    created_by: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_transactions",
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["variant"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.transaction_type} - {self.variant.sku} ({self.quantity_changed})"
