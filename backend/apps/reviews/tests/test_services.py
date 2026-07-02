from __future__ import annotations

import pytest

from apps.common.exceptions import BusinessRuleViolation
from apps.reviews.factories import ReviewFactory
from apps.reviews.models import ReviewStatus
from apps.reviews.services.moderation import approve_review, reject_review

pytestmark = pytest.mark.django_db


class TestApproveReview:
    def test_approves_pending_review(self, admin_user):
        review = ReviewFactory(status=ReviewStatus.PENDING)

        result = approve_review(review=review, approved_by=admin_user)

        result.refresh_from_db()
        assert result.status == ReviewStatus.APPROVED
        assert result.approved_at is not None

    def test_raises_on_non_pending_review(self, admin_user):
        review = ReviewFactory(status=ReviewStatus.APPROVED)

        with pytest.raises(BusinessRuleViolation) as exc:
            approve_review(review=review, approved_by=admin_user)

        assert exc.value.code == "invalid_review_status"


class TestRejectReview:
    def test_rejects_pending_review(self):
        review = ReviewFactory(status=ReviewStatus.PENDING)

        result = reject_review(review=review)

        result.refresh_from_db()
        assert result.status == ReviewStatus.REJECTED

    def test_raises_on_already_approved(self):
        review = ReviewFactory(status=ReviewStatus.APPROVED)

        with pytest.raises(BusinessRuleViolation) as exc:
            reject_review(review=review)

        assert exc.value.code == "invalid_review_status"
