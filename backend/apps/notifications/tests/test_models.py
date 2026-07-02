from __future__ import annotations

import pytest

from apps.notifications.factories import NotificationFactory, NotificationPreferenceFactory
from apps.notifications.models import Notification, NotificationPreference

pytestmark = pytest.mark.django_db


class TestNotificationPreference:
    def test_create_prefs(self):
        NotificationPreferenceFactory()
        assert NotificationPreference.objects.count() == 1


class TestNotification:
    def test_create_notification(self):
        NotificationFactory()
        assert Notification.objects.count() == 1
