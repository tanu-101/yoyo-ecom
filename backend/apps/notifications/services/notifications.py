from __future__ import annotations

from django.db import transaction

from apps.accounts.models import User
from apps.notifications.models import NotificationPreference
from apps.notifications.selectors.notifications import get_preferences_for_user


@transaction.atomic
def update_preferences(*, user: User, data: dict) -> NotificationPreference:
    allowed_fields = {
        "order_updates_email",
        "order_updates_sms",
        "promotions_email",
        "promotions_sms",
    }

    pref = get_preferences_for_user(user=user)

    for field, value in data.items():
        if field in allowed_fields and isinstance(value, bool):
            setattr(pref, field, value)

    pref.save(update_fields=[f for f in data if f in allowed_fields])
    return pref
