from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import TimeStampedModel


class NotificationPreference(TimeStampedModel):
    user: models.OneToOneField = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    order_updates_email: models.BooleanField = models.BooleanField(default=True)
    order_updates_sms: models.BooleanField = models.BooleanField(default=False)
    promotions_email: models.BooleanField = models.BooleanField(default=True)
    promotions_sms: models.BooleanField = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Preferences for {self.user.email}"
