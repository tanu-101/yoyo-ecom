from __future__ import annotations

from rest_framework import serializers

from apps.reviews.models import Review, ReviewImage


class PublicReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ["image"]


class PublicReviewSerializer(serializers.ModelSerializer):
    images = PublicReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "customer",
            "rating",
            "title",
            "content",
            "helpful_count",
            "unhelpful_count",
            "images",
            "created_at",
        ]
