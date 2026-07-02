from __future__ import annotations

from rest_framework import serializers


class SalesQuerySerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    group_by = serializers.ChoiceField(choices=["day", "week", "month"], default="day")


class TopProductsQuerySerializer(serializers.Serializer):
    limit = serializers.IntegerField(default=10, min_value=1, max_value=100)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
