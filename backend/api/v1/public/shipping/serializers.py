from __future__ import annotations

from rest_framework import serializers

from apps.shipping.models import ShippingMethod


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = [
            "id",
            "name",
            "code",
            "description",
            "base_price",
            "price_per_kg",
            "estimated_min_days",
            "estimated_max_days",
        ]
