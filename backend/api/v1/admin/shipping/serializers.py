from __future__ import annotations

from rest_framework import serializers


class AdminTrackingSerializer(serializers.Serializer):
    carrier = serializers.CharField(max_length=255)
    tracking_number = serializers.CharField(max_length=255)
    tracking_url = serializers.URLField(required=False, allow_blank=True)
    estimated_delivery = serializers.DateField(required=False, allow_null=True)


class AdminTrackingUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            "processing",
            "in_transit",
            "out_for_delivery",
            "delivered",
            "exception",
        ]
    )
    tracking_url = serializers.URLField(required=False, allow_blank=True)
