from __future__ import annotations

from rest_framework import serializers

from apps.reviews.models import Review, ReviewImage


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ["image"]


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "customer",
            "order_item",
            "rating",
            "title",
            "content",
            "status",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["customer", "status", "created_at", "updated_at"]


class CreateReviewSerializer(serializers.Serializer):
    order_item = serializers.UUIDField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    title = serializers.CharField(max_length=255)
    content = serializers.CharField(max_length=5000, required=False, allow_blank=True)
    images = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, default=list
    )
