from __future__ import annotations

from rest_framework import serializers

from apps.coupons.models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "description",
            "discount_type",
            "discount_value",
            "min_order_value",
            "max_discount_amount",
            "max_usage_count",
            "usage_count",
            "per_customer_limit",
            "valid_from",
            "valid_until",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["usage_count", "created_at", "updated_at"]


class CouponCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "code",
            "description",
            "discount_type",
            "discount_value",
            "min_order_value",
            "max_discount_amount",
            "max_usage_count",
            "per_customer_limit",
            "valid_from",
            "valid_until",
            "is_active",
        ]
