from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.notifications.models import Notification, NotificationPreference


def get_notifications_for_user(*, user: User) -> QuerySet[Notification]:
    return Notification.objects.filter(user=user)


def get_preferences_for_user(*, user: User) -> NotificationPreference:
    pref, _ = NotificationPreference.objects.get_or_create(user=user)
    return pref
