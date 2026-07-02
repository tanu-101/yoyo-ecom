from __future__ import annotations

from django.db import models

from apps.catalog.constants import VariantStatus
from apps.common.models.base import SoftDeleteModel


class Variant(SoftDeleteModel):
    product: models.ForeignKey = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="variants",
    )
    sku: models.CharField = models.CharField(max_length=100, unique=True)
    name: models.CharField = models.CharField(max_length=255)
    price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity: models.IntegerField = models.IntegerField(default=0)
    status: models.CharField = models.CharField(
        max_length=20,
        choices=VariantStatus.choices,
        default=VariantStatus.ACTIVE,
    )
    image: models.URLField = models.URLField(blank=True, default="")

    class Meta:
        ordering = ["product", "sku"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["status"]),
            models.Index(fields=["product", "status"]),
            models.Index(fields=["product", "stock_quantity"]),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.name} ({self.sku})"
