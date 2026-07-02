from __future__ import annotations

from rest_framework import serializers

from apps.catalog.models import (
    Category,
    Product,
    ProductImage,
    Variant,
    VariantAttribute,
    VariantAttributeValue,
)


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "image",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdminProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "product", "image", "alt_text", "sort_order", "is_primary"]


class AdminVariantAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantAttribute
        fields = ["id", "name", "slug"]


class AdminVariantAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantAttributeValue
        fields = ["id", "attribute", "value", "slug"]


class AdminVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = [
            "id",
            "product",
            "sku",
            "name",
            "price",
            "stock_quantity",
            "status",
            "image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdminProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "name",
            "slug",
            "description",
            "base_price",
            "status",
            "is_featured",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
