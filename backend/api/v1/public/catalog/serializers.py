from __future__ import annotations

from rest_framework import serializers

from apps.catalog.models import (
    Category,
    Product,
    ProductImage,
    Variant,
    VariantAttributeValue,
    VariantOption,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "image", "parent"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_primary"]


class VariantAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source="attribute.name")

    class Meta:
        model = VariantAttributeValue
        fields = ["id", "attribute_name", "value", "slug"]


class VariantOptionSerializer(serializers.ModelSerializer):
    attribute = serializers.CharField(source="attribute.name")
    value = serializers.CharField(source="value.value")

    class Meta:
        model = VariantOption
        fields = ["attribute", "value"]


class VariantSerializer(serializers.ModelSerializer):
    options = VariantOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Variant
        fields = ["id", "sku", "name", "price", "stock_quantity", "image", "options"]


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "category", "name", "slug", "base_price", "primary_image", "is_featured"]

    def get_primary_image(self, obj: Product) -> str | None:
        image = obj.images.filter(is_primary=True).first()
        if image:
            return image.image
        image = obj.images.first()
        return image.image if image else None


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    images = ProductImageSerializer(many=True)
    variants = VariantSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "name",
            "slug",
            "description",
            "base_price",
            "images",
            "variants",
            "is_featured",
        ]
