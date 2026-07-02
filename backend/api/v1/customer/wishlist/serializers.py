from __future__ import annotations

from rest_framework import serializers

from apps.catalog.models import Product, Variant
from apps.wishlist.models import WishlistItem


class ProductBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "base_price"]


class VariantBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ["id", "name", "sku", "price"]


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductBriefSerializer(read_only=True)
    variant = VariantBriefSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "variant", "notes", "created_at"]


class AddWishlistItemSerializer(serializers.Serializer):
    product = serializers.UUIDField()
    variant = serializers.UUIDField(required=False, allow_null=True)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class MoveToCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(default=1, min_value=1)
