from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.catalog.constants import ProductStatus
from apps.common.models.base import SoftDeleteModel


class Product(SoftDeleteModel):
    category: models.ForeignKey = models.ForeignKey(
        "catalog.Category",
        on_delete=models.CASCADE,
        related_name="products",
    )
    name: models.CharField = models.CharField(max_length=255)
    slug: models.SlugField = models.SlugField(max_length=255, unique=True)
    description: models.TextField = models.TextField()
    base_price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    status: models.CharField = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
    )
    is_featured: models.BooleanField = models.BooleanField(default=False)
    created_by: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_products",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self) -> str:
        return self.name
