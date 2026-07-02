from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User
from apps.orders.models import Order, OrderItem, OrderStatusHistory


class AdminOrderItemSerializer(serializers.ModelSerializer):
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


class AdminOrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ["id", "from_status", "to_status", "changed_by", "reason", "created_at"]


class CustomerBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class AdminOrderListSerializer(serializers.ModelSerializer):
    customer = CustomerBriefSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer",
            "status",
            "payment_status",
            "subtotal",
            "total_amount",
            "created_at",
            "updated_at",
        ]


class AdminOrderDetailSerializer(serializers.ModelSerializer):
    items = AdminOrderItemSerializer(many=True, read_only=True)
    status_history = AdminOrderStatusHistorySerializer(many=True, read_only=True)
    customer = CustomerBriefSerializer(read_only=True)

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
            "cancelled_by",
            "cancellation_reason",
            "items",
            "status_history",
            "created_at",
            "updated_at",
        ]


class AdminUpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            "placed",
            "processing",
            "shipped",
            "delivered",
        ]
    )
    reason = serializers.CharField(max_length=2000, required=False, allow_blank=True)


class AdminCancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=2000, required=False, allow_blank=True)
