from __future__ import annotations

from django.core.mail import send_mail
from django.utils import timezone

from apps.accounts.models import User
from apps.notifications.constants import NotificationChannel, NotificationStatus
from apps.notifications.models import Notification
from apps.notifications.selectors.notifications import get_preferences_for_user
from apps.notifications.services.sms import send_sms


def dispatch_notification(
    *,
    user: User,
    notification_type: str,
    subject: str = "",
    body: str,
    channel: str = NotificationChannel.IN_APP,
) -> Notification:
    notification = Notification.objects.create(
        user=user,
        channel=channel,
        notification_type=notification_type,
        subject=subject,
        body=body,
        status=NotificationStatus.PENDING,
    )

    if channel == NotificationChannel.EMAIL:
        try:
            send_mail(
                subject,
                body,
                None,
                [user.email],
                fail_silently=False,
            )
            notification.status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
        except Exception as exc:
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(exc)

    elif channel == NotificationChannel.SMS:
        if user.phone:
            success = send_sms(to=user.phone, body=body)
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = timezone.now()
            else:
                notification.status = NotificationStatus.FAILED
                notification.error_message = "SMS sending failed"
        else:
            notification.status = NotificationStatus.FAILED
            notification.error_message = "No phone number on file"

    else:
        notification.status = NotificationStatus.SENT
        notification.sent_at = timezone.now()

    notification.save(update_fields=["status", "sent_at", "error_message", "updated_at"])
    return notification


def dispatch_order_notifications(
    *, user: User, notification_type: str, subject: str, body: str
) -> list[Notification]:
    notifications: list[Notification] = []
    prefs = get_preferences_for_user(user=user)

    if prefs.order_updates_email:
        n = dispatch_notification(
            user=user,
            notification_type=notification_type,
            subject=subject,
            body=body,
            channel=NotificationChannel.EMAIL,
        )
        notifications.append(n)

    if prefs.order_updates_sms:
        n = dispatch_notification(
            user=user,
            notification_type=notification_type,
            subject=subject,
            body=body,
            channel=NotificationChannel.SMS,
        )
        notifications.append(n)

    n = dispatch_notification(
        user=user,
        notification_type=notification_type,
        subject=subject,
        body=body,
        channel=NotificationChannel.IN_APP,
    )
    notifications.append(n)

    return notifications
