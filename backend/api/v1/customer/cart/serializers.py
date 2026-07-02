from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from apps.carts.models.cart import Cart
from apps.carts.models.cart_item import CartItem


class CartItemVariantSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    sku = serializers.CharField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image = serializers.CharField()
    stock_quantity = serializers.IntegerField()


class CartItemProductSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()


class CartItemSerializer(serializers.ModelSerializer[CartItem]):
    variant = CartItemVariantSerializer(read_only=True)
    product = CartItemProductSerializer(read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "variant", "quantity", "unit_price", "line_total", "updated_at"]
        read_only_fields = fields

    def get_line_total(self, obj: CartItem) -> Decimal:
        return obj.unit_price * obj.quantity


class CartTotalsSerializer(serializers.Serializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    item_count = serializers.IntegerField()


class CartSerializer(serializers.ModelSerializer[Cart]):
    items = CartItemSerializer(many=True, read_only=True)
    totals = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "totals", "updated_at"]
        read_only_fields = fields

    def get_totals(self, obj: Cart) -> dict:
        from apps.carts.selectors.carts import calculate_cart_totals

        return CartTotalsSerializer(calculate_cart_totals(cart=obj)).data


class AddCartItemSerializer(serializers.Serializer):
    variant_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
