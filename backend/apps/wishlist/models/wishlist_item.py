from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import TimeStampedModel


class WishlistItem(TimeStampedModel):
    customer: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    product: models.ForeignKey = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    variant: models.ForeignKey = models.ForeignKey(
        "catalog.Variant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wishlist_items",
    )
    notes: models.TextField = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "product", "variant"],
                name="unique_customer_product_variant",
            ),
        ]
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["product"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.customer.email}"
