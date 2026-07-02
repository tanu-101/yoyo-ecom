from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.common.exceptions import BusinessRuleViolation
from apps.reviews.models import Review, ReviewStatus


@transaction.atomic
def approve_review(*, review: Review, approved_by: User | None = None) -> Review:
    if review.status != ReviewStatus.PENDING:
        raise BusinessRuleViolation(
            "Only pending reviews can be approved.",
            code="invalid_review_status",
        )

    review.status = ReviewStatus.APPROVED
    review.approved_at = timezone.now()
    review.save(update_fields=["status", "approved_at", "updated_at"])
    return review


@transaction.atomic
def reject_review(*, review: Review) -> Review:
    if review.status != ReviewStatus.PENDING:
        raise BusinessRuleViolation(
            "Only pending reviews can be rejected.",
            code="invalid_review_status",
        )

    review.status = ReviewStatus.REJECTED
    review.save(update_fields=["status", "updated_at"])
    return review
