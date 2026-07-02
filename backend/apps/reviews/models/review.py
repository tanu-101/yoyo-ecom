from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import TimeStampedModel


class ReviewStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class Review(TimeStampedModel):
    product: models.ForeignKey = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    customer: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    order_item: models.OneToOneField = models.OneToOneField(
        "orders.OrderItem",
        on_delete=models.CASCADE,
        related_name="review",
    )
    rating: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField()
    title: models.CharField = models.CharField(max_length=255)
    content: models.TextField = models.TextField(blank=True, default="")
    status: models.CharField = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )
    helpful_count: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    unhelpful_count: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    approved_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["status"]),
            models.Index(fields=["product", "status"]),
        ]

    def __str__(self) -> str:
        return self.title
