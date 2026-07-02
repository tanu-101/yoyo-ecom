from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from apps.orders.models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "variant",
            "product_name",
            "variant_name",
            "sku",
            "quantity",
            "unit_price",
            "line_total",
            "created_at",
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ["id", "from_status", "to_status", "changed_by", "reason", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer",
            "status",
            "payment_status",
            "subtotal",
            "discount_amount",
            "shipping_cost",
            "tax_amount",
            "total_amount",
            "customer_notes",
            "admin_notes",
            "placed_at",
            "paid_at",
            "shipped_at",
            "delivered_at",
            "cancelled_at",
            "cancellation_reason",
            "items",
            "status_history",
            "created_at",
            "updated_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    shipping_cost = serializers.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    customer_notes = serializers.CharField(max_length=2000, required=False, allow_blank=True)


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=2000, required=False, allow_blank=True)
