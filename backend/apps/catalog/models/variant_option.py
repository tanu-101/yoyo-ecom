from __future__ import annotations

from django.db import models

from apps.common.models.base import TimeStampedModel


class VariantOption(TimeStampedModel):
    variant: models.ForeignKey = models.ForeignKey(
        "catalog.Variant",
        on_delete=models.CASCADE,
        related_name="options",
    )
    attribute: models.ForeignKey = models.ForeignKey(
        "catalog.VariantAttribute",
        on_delete=models.CASCADE,
        related_name="options",
    )
    value: models.ForeignKey = models.ForeignKey(
        "catalog.VariantAttributeValue",
        on_delete=models.CASCADE,
        related_name="options",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["variant", "attribute"], name="unique_variant_attribute"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.variant.sku}: {self.attribute.name}={self.value.value}"
