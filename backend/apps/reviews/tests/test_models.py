from __future__ import annotations

import pytest

from apps.reviews.factories import ReviewFactory
from apps.reviews.models import Review

pytestmark = pytest.mark.django_db


class TestReviewModel:
    def test_create_review(self):
        review = ReviewFactory()
        assert Review.objects.count() == 1
        assert str(review) == review.title
