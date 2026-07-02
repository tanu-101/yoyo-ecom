from __future__ import annotations

from rest_framework import serializers

from apps.notifications.models import Notification, NotificationPreference


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "order_updates_email",
            "order_updates_sms",
            "promotions_email",
            "promotions_sms",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "channel",
            "notification_type",
            "subject",
            "body",
            "status",
            "sent_at",
            "created_at",
        ]
