from __future__ import annotations

from rest_framework import serializers

from apps.payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "provider",
            "amount",
            "currency",
            "status",
            "failure_reason",
            "created_at",
            "processed_at",
        ]


class CreatePaymentIntentSerializer(serializers.Serializer):
    order = serializers.UUIDField()
