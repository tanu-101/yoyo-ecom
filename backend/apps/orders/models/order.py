from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import TimeStampedModel
from apps.orders.constants import OrderStatus, PaymentStatus


class Order(TimeStampedModel):
    order_number: models.CharField = models.CharField(max_length=50, unique=True)
    customer: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status: models.CharField = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING_PAYMENT,
    )
    payment_status: models.CharField = models.CharField(
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    subtotal: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    shipping_cost: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    tax_amount: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    total_amount: models.DecimalField = models.DecimalField(max_digits=12, decimal_places=2)
    customer_notes: models.TextField = models.TextField(blank=True, default="")
    admin_notes: models.TextField = models.TextField(blank=True, default="")
    placed_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    paid_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    shipped_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    delivered_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    cancelled_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    cancelled_by: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancelled_orders",
    )
    cancellation_reason: models.TextField = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["status"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["customer", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.order_number
