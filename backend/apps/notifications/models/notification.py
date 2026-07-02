from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import TimeStampedModel


class NotificationChannel(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    IN_APP = "in_app", "In app"


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"


class Notification(TimeStampedModel):
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    channel: models.CharField = models.CharField(max_length=20, choices=NotificationChannel.choices)
    notification_type: models.CharField = models.CharField(max_length=100)
    subject: models.CharField = models.CharField(max_length=255, blank=True, default="")
    body: models.TextField = models.TextField()
    status: models.CharField = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )
    sent_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    error_message: models.TextField = models.TextField(blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["channel"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.notification_type} - {self.user.email}"
