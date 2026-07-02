from __future__ import annotations

from django.db import models

from apps.common.models.base import TimeStampedModel


class OrderItem(TimeStampedModel):
    order: models.ForeignKey = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product: models.ForeignKey = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    variant: models.ForeignKey = models.ForeignKey(
        "catalog.Variant",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    product_name: models.CharField = models.CharField(max_length=255)
    variant_name: models.CharField = models.CharField(max_length=255)
    sku: models.CharField = models.CharField(max_length=100)
    quantity: models.PositiveIntegerField = models.PositiveIntegerField()
    unit_price: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)
    line_total: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["variant"]),
        ]

    def __str__(self) -> str:
        return f"{self.sku} x {self.quantity}"
