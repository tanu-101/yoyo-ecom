from __future__ import annotations

from django.contrib import admin

from apps.notifications.models import Notification, NotificationPreference


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "order_updates_email", "promotions_email")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "channel", "notification_type", "status", "created_at")
    list_filter = ("channel", "status", "notification_type")
