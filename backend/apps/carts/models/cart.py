from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import TimeStampedModel


class Cart(TimeStampedModel):
    customer: models.OneToOneField = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    class Meta:
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["updated_at"]),
        ]

    def __str__(self) -> str:
        return f"Cart({self.customer.email})"
