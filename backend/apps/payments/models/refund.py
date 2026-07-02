from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import TimeStampedModel
from apps.payments.constants import RefundState


class Refund(TimeStampedModel):
    payment: models.ForeignKey = models.ForeignKey(
        "payments.Payment",
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    order: models.ForeignKey = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    return_request: models.ForeignKey = models.ForeignKey(
        "returns.ReturnRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds",
    )
    provider_refund_id: models.CharField = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    amount: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)
    reason: models.TextField = models.TextField(blank=True, default="")
    status: models.CharField = models.CharField(
        max_length=20,
        choices=RefundState.choices,
        default=RefundState.PENDING,
    )
    created_by: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiated_refunds",
    )
    processed_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payment"]),
            models.Index(fields=["order"]),
            models.Index(fields=["return_request"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Refund {self.id} - {self.status}"
