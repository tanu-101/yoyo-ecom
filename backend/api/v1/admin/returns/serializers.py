from __future__ import annotations

from rest_framework import serializers

from apps.returns.models import ReturnResolution


class AdminApproveReturnSerializer(serializers.Serializer):
    resolution = serializers.ChoiceField(choices=ReturnResolution.choices)
    refund_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True
    )
    admin_notes = serializers.CharField(max_length=2000, required=False, allow_blank=True)


class AdminRejectReturnSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(max_length=2000)
    admin_notes = serializers.CharField(max_length=2000, required=False, allow_blank=True)
