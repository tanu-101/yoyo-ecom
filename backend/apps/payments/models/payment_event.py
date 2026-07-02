from __future__ import annotations

from django.db import models

from apps.common.models.base import UUIDModel
from apps.payments.constants import PaymentProvider


class PaymentEvent(UUIDModel):
    provider: models.CharField = models.CharField(
        max_length=30,
        choices=PaymentProvider.choices,
    )
    event_id: models.CharField = models.CharField(max_length=255, unique=True)
    event_type: models.CharField = models.CharField(max_length=255)
    payload: models.JSONField = models.JSONField()
    processed_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    processing_error: models.TextField = models.TextField(blank=True, default="")
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_id"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["processed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} ({self.event_id})"
