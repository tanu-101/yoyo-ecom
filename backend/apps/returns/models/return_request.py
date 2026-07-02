from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import TimeStampedModel


class ReturnStatus(models.TextChoices):
    PENDING_REVIEW = "pending_review", "Pending review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    AWAITING_RETURN = "awaiting_return", "Awaiting return"
    IN_TRANSIT = "in_transit", "In transit"
    RECEIVED = "received", "Received"
    PROCESSED = "processed", "Processed"
    REFUNDED = "refunded", "Refunded"
    REPLACED = "replaced", "Replaced"
    COMPLETED = "completed", "Completed"


class ReturnReason(models.TextChoices):
    DAMAGED = "damaged", "Damaged"
    WRONG_ITEM = "wrong_item", "Wrong item"
    MISSING_ITEM = "missing_item", "Missing item"
    DEFECTIVE = "defective", "Defective"
    OTHER = "other", "Other"


class ReturnResolution(models.TextChoices):
    REFUND = "refund", "Refund"
    REPLACEMENT = "replacement", "Replacement"
    STORE_CREDIT = "store_credit", "Store credit"


class ReturnRequest(TimeStampedModel):
    return_number: models.CharField = models.CharField(max_length=50, unique=True)
    order: models.ForeignKey = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="return_requests",
    )
    customer: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="return_requests",
    )
    status: models.CharField = models.CharField(
        max_length=30,
        choices=ReturnStatus.choices,
        default=ReturnStatus.PENDING_REVIEW,
    )
    reason: models.CharField = models.CharField(
        max_length=30,
        choices=ReturnReason.choices,
    )
    resolution: models.CharField = models.CharField(  # noqa: DJ001
        max_length=30,
        choices=ReturnResolution.choices,
        null=True,
        blank=True,
    )
    comments: models.TextField = models.TextField(blank=True, default="")
    admin_notes: models.TextField = models.TextField(blank=True, default="")
    rejection_reason: models.TextField = models.TextField(blank=True, default="")
    refund_amount: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    reviewed_by: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_returns",
    )
    reviewed_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    received_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    completed_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["return_number"]),
            models.Index(fields=["order"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return self.return_number
