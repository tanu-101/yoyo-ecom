from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import TimeStampedModel


class VoteType(models.TextChoices):
    HELPFUL = "helpful", "Helpful"
    UNHELPFUL = "unhelpful", "Unhelpful"


class ReviewVote(TimeStampedModel):
    review: models.ForeignKey = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="votes",
    )
    customer: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_votes",
    )
    vote: models.CharField = models.CharField(max_length=20, choices=VoteType.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["review", "customer"], name="unique_review_vote"),
        ]

    def __str__(self) -> str:
        return f"{self.vote} by {self.customer.email}"
