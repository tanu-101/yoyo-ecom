from __future__ import annotations

import factory

from apps.accounts.factories import CustomerUserFactory
from apps.notifications.models import Notification, NotificationPreference


class NotificationPreferenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NotificationPreference
        django_get_or_create = ("user",)

    user = factory.SubFactory(CustomerUserFactory)


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(CustomerUserFactory)
    channel = "email"
    notification_type = "order_confirmation"
    subject = "Order confirmed"
    body = "Your order has been confirmed."
