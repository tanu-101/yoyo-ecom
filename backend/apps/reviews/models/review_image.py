from __future__ import annotations

from django.db import models

from apps.common.models.base import UUIDModel


class ReviewImage(UUIDModel):
    review: models.ForeignKey = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image: models.CharField = models.CharField(max_length=500)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Image for review {self.review_id}"
