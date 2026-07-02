from __future__ import annotations

from django.db import models

from apps.common.models.base import SoftDeleteModel


class Category(SoftDeleteModel):
    name: models.CharField = models.CharField(max_length=255)
    slug: models.SlugField = models.SlugField(max_length=255, unique=True)
    description: models.TextField = models.TextField(blank=True, default="")
    parent: models.ForeignKey = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    image: models.URLField = models.URLField(blank=True, default="")
    is_active: models.BooleanField = models.BooleanField(default=True)
    sort_order: models.PositiveIntegerField = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.name
