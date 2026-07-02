from __future__ import annotations

from unittest.mock import patch

import pytest

from apps.notifications.constants import NotificationChannel, NotificationStatus
from apps.notifications.models import NotificationPreference
from apps.notifications.services.dispatch import (
    dispatch_notification,
    dispatch_order_notifications,
)

pytestmark = pytest.mark.django_db


class TestDispatchNotification:
    def test_dispatch_email_sends_mail_and_marks_sent(self, customer_user):
        with patch(
            "apps.notifications.services.dispatch.send_mail",
        ) as mock_send_mail:
            notification = dispatch_notification(
                user=customer_user,
                notification_type="test",
                subject="Hello",
                body="Test body",
                channel=NotificationChannel.EMAIL,
            )

        mock_send_mail.assert_called_once_with(
            "Hello",
            "Test body",
            None,
            [customer_user.email],
            fail_silently=False,
        )
        notification.refresh_from_db()
        assert notification.status == NotificationStatus.SENT
        assert notification.sent_at is not None

    def test_dispatch_email_marks_failed_on_error(self, customer_user):
        with patch(
            "apps.notifications.services.dispatch.send_mail",
            side_effect=Exception("SMTP error"),
        ):
            notification = dispatch_notification(
                user=customer_user,
                notification_type="test",
                subject="Hello",
                body="Test body",
                channel=NotificationChannel.EMAIL,
            )

        notification.refresh_from_db()
        assert notification.status == NotificationStatus.FAILED
        assert "SMTP error" in notification.error_message

    def test_dispatch_sms_sends_and_marks_sent(self, customer_user):
        customer_user.phone = "+8801700000000"
        customer_user.save()

        with patch(
            "apps.notifications.services.dispatch.send_sms",
            return_value=True,
        ) as mock_sms:
            notification = dispatch_notification(
                user=customer_user,
                notification_type="test",
                subject="SMS Subject",
                body="SMS body",
                channel=NotificationChannel.SMS,
            )

        mock_sms.assert_called_once_with(
            to="+8801700000000",
            body="SMS body",
        )
        notification.refresh_from_db()
        assert notification.status == NotificationStatus.SENT

    def test_dispatch_sms_fails_if_no_phone(self, customer_user):
        customer_user.phone = ""
        customer_user.save()

        notification = dispatch_notification(
            user=customer_user,
            notification_type="test",
            subject="SMS",
            body="Body",
            channel=NotificationChannel.SMS,
        )

        notification.refresh_from_db()
        assert notification.status == NotificationStatus.FAILED
        assert "No phone number" in notification.error_message

    def test_dispatch_in_app_marks_sent_immediately(self, customer_user):
        notification = dispatch_notification(
            user=customer_user,
            notification_type="test",
            subject="In app",
            body="In app body",
            channel=NotificationChannel.IN_APP,
        )

        notification.refresh_from_db()
        assert notification.status == NotificationStatus.SENT
        assert notification.sent_at is not None


class TestDispatchOrderNotifications:
    def test_dispatches_to_all_enabled_channels(self, customer_user):
        NotificationPreference.objects.create(
            user=customer_user,
            order_updates_email=True,
            order_updates_sms=False,
            promotions_email=True,
            promotions_sms=False,
        )

        with patch(
            "apps.notifications.services.dispatch.send_mail",
        ):
            notifications = dispatch_order_notifications(
                user=customer_user,
                notification_type="order_confirmation",
                subject="Order confirmed",
                body="Your order is placed.",
            )

        assert len(notifications) == 2  # email + in_app (sms is disabled)
        channels = [n.channel for n in notifications]
        assert NotificationChannel.EMAIL in channels
        assert NotificationChannel.IN_APP in channels
        assert NotificationChannel.SMS not in channels

    def test_dispatches_sms_if_enabled(self, customer_user):
        customer_user.phone = "+8801700000000"
        customer_user.save()
        NotificationPreference.objects.create(
            user=customer_user,
            order_updates_email=False,
            order_updates_sms=True,
        )

        with (
            patch("apps.notifications.services.dispatch.send_mail"),
            patch(
                "apps.notifications.services.dispatch.send_sms",
                return_value=True,
            ),
        ):
            notifications = dispatch_order_notifications(
                user=customer_user,
                notification_type="order_shipped",
                subject="Shipped",
                body="Your order has shipped.",
            )

        assert len(notifications) == 2  # sms + in_app
        channels = [n.channel for n in notifications]
        assert NotificationChannel.SMS in channels
        assert NotificationChannel.IN_APP in channels
