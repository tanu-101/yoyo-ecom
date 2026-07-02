from __future__ import annotations

from django.db import models

from apps.carts.models.cart import Cart
from apps.common.models.base import TimeStampedModel


class CartItem(TimeStampedModel):
    cart: models.ForeignKey = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product: models.ForeignKey = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    variant: models.ForeignKey = models.ForeignKey(
        "catalog.Variant",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(default=1)
    # Snapshot of price at the time item was added; refreshed on re-add
    unit_price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "variant"], name="unique_cart_variant"),
        ]
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["variant"]),
        ]

    def __str__(self) -> str:
        return f"CartItem({self.variant.sku} x{self.quantity})"

    @property
    def line_total(self) -> float:
        return float(self.unit_price) * self.quantity
