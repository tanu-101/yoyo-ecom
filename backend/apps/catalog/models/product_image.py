from __future__ import annotations

from django.db import models

from apps.common.models.base import TimeStampedModel


class ProductImage(TimeStampedModel):
    product: models.ForeignKey = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image: models.URLField = models.URLField()
    alt_text: models.CharField = models.CharField(max_length=255, blank=True, default="")
    sort_order: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    is_primary: models.BooleanField = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "created_at"]
        indexes = [
            models.Index(fields=["product", "is_primary"]),
        ]

    def __str__(self) -> str:
        return f"Image for {self.product.name}"
