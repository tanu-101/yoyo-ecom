from __future__ import annotations

from rest_framework import serializers

from apps.returns.models import ReturnImage, ReturnItem, ReturnRequest, ReturnStatusHistory


class ReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnItem
        fields = ["order_item", "quantity", "reason", "condition_notes"]


class ReturnImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnImage
        fields = ["image"]


class ReturnStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnStatusHistory
        fields = ["from_status", "to_status", "reason", "created_at"]


class ReturnRequestSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, read_only=True)
    images = ReturnImageSerializer(many=True, read_only=True)
    status_history = ReturnStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = ReturnRequest
        fields = [
            "id",
            "return_number",
            "order",
            "customer",
            "status",
            "reason",
            "resolution",
            "comments",
            "admin_notes",
            "rejection_reason",
            "refund_amount",
            "items",
            "images",
            "status_history",
            "created_at",
            "updated_at",
        ]


class CreateReturnSerializer(serializers.Serializer):
    order = serializers.UUIDField()
    reason = serializers.ChoiceField(
        choices=[
            "damaged",
            "wrong_item",
            "missing_item",
            "defective",
            "other",
        ]
    )
    comments = serializers.CharField(max_length=2000, required=False, allow_blank=True)
    resolution = serializers.ChoiceField(choices=["refund", "replacement", "store_credit"])
    items = ReturnItemSerializer(many=True)
    images = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, default=list
    )
