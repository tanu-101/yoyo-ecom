from __future__ import annotations

from rest_framework import serializers

from apps.notifications.models import Notification, NotificationPreference


class AdminNotificationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "user_email",
            "channel",
            "notification_type",
            "subject",
            "body",
            "status",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "user", "user_email", "sent_at", "created_at"]


class AdminNotificationPreferenceSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = NotificationPreference
        fields = [
            "id",
            "user",
            "user_email",
            "order_updates_email",
            "order_updates_sms",
            "promotions_email",
            "promotions_sms",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "user_email", "created_at", "updated_at"]
