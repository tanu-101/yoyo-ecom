from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import UUIDModel


class ReturnStatusHistory(UUIDModel):
    return_request: models.ForeignKey = models.ForeignKey(
        "returns.ReturnRequest",
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    from_status: models.CharField = models.CharField(max_length=30, blank=True, default="")
    to_status: models.CharField = models.CharField(max_length=30)
    changed_by: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="return_status_changes",
    )
    reason: models.TextField = models.TextField(blank=True, default="")
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.from_status} -> {self.to_status}"
