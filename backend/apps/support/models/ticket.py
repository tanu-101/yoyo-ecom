from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import SoftDeleteModel


class Ticket(SoftDeleteModel):
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_tickets",
    )
    subject: models.CharField = models.CharField(max_length=255)
    message: models.TextField = models.TextField()
    is_resolved: models.BooleanField = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user.email} - {self.subject}"
