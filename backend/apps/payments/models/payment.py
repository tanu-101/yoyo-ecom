from __future__ import annotations

from django.db import models

from apps.common.models.base import TimeStampedModel
from apps.payments.constants import PaymentProvider, PaymentState


class Payment(TimeStampedModel):
    order: models.ForeignKey = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payments",
    )
    provider: models.CharField = models.CharField(
        max_length=30,
        choices=PaymentProvider.choices,
        default=PaymentProvider.STRIPE,
    )
    provider_payment_intent_id: models.CharField = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    provider_charge_id: models.CharField = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    amount: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)
    currency: models.CharField = models.CharField(max_length=3, default="USD")
    status: models.CharField = models.CharField(
        max_length=20,
        choices=PaymentState.choices,
        default=PaymentState.PENDING,
    )
    failure_reason: models.TextField = models.TextField(blank=True, default="")
    metadata: models.JSONField = models.JSONField(null=True, blank=True)
    processed_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["provider_payment_intent_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Payment {self.id} - {self.status}"
