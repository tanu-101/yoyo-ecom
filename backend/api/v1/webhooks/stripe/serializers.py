from __future__ import annotations

from rest_framework import serializers


class StripeWebhookSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    data = serializers.JSONField()
    created = serializers.IntegerField(required=False)
    livemode = serializers.BooleanField(required=False, default=False)
    pending_webhooks = serializers.IntegerField(required=False)
    request = serializers.JSONField(required=False)
    api_version = serializers.CharField(required=False)
    account = serializers.CharField(required=False)
