from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.reviews.models import Review


def get_approved_reviews_for_product(*, product_id: UUID) -> QuerySet[Review]:
    return Review.objects.filter(
        product_id=product_id,
        status="approved",
    ).order_by("-created_at")


def get_review_by_id(review_id: str | UUID) -> Review | None:
    return Review.objects.select_related("customer", "product").filter(id=review_id).first()


def get_reviews_for_admin() -> QuerySet[Review]:
    return Review.objects.select_related("customer", "product").order_by("-created_at")
