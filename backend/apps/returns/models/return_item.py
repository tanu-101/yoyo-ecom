from __future__ import annotations

from django.db import models

from apps.common.models.base import TimeStampedModel


class ReturnItem(TimeStampedModel):
    return_request: models.ForeignKey = models.ForeignKey(
        "returns.ReturnRequest",
        on_delete=models.CASCADE,
        related_name="items",
    )
    order_item: models.ForeignKey = models.ForeignKey(
        "orders.OrderItem",
        on_delete=models.PROTECT,
        related_name="return_items",
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField()
    reason: models.CharField = models.CharField(
        max_length=30,
        choices=[
            ("damaged", "Damaged"),
            ("wrong_item", "Wrong item"),
            ("missing_item", "Missing item"),
            ("defective", "Defective"),
            ("other", "Other"),
        ],
    )
    condition_notes: models.TextField = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["return_request", "order_item"], name="unique_return_item"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.order_item.sku} x {self.quantity}"
