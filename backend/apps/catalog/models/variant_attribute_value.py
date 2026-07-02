from __future__ import annotations

from django.db import models

from apps.common.models.base import TimeStampedModel


class VariantAttributeValue(TimeStampedModel):
    attribute: models.ForeignKey = models.ForeignKey(
        "catalog.VariantAttribute",
        on_delete=models.CASCADE,
        related_name="values",
    )
    value: models.CharField = models.CharField(max_length=100)
    slug: models.SlugField = models.SlugField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["attribute", "value"], name="unique_attribute_value"),
            models.UniqueConstraint(fields=["attribute", "slug"], name="unique_attribute_slug"),
        ]

    def __str__(self) -> str:
        return f"{self.attribute.name}: {self.value}"
