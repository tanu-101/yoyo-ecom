from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User
from apps.orders.models import Order
from apps.payments.models import Payment


class AdminOrderBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "order_number"]


class AdminCustomerBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class AdminPaymentSerializer(serializers.ModelSerializer):
    order = AdminOrderBriefSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "provider",
            "provider_payment_intent_id",
            "amount",
            "currency",
            "status",
            "failure_reason",
            "created_at",
            "processed_at",
            "updated_at",
        ]


class AdminRefundSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(max_length=2000, required=False, allow_blank=True)
