from __future__ import annotations

from django.db import models

from apps.common.models.base import UUIDModel


class ReturnImage(UUIDModel):
    return_request: models.ForeignKey = models.ForeignKey(
        "returns.ReturnRequest",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image: models.CharField = models.CharField(max_length=500)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Image for {self.return_request.return_number}"
