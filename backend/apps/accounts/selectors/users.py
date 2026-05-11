from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.models import User


def active_users() -> QuerySet[User]:
    return User.objects.filter(is_active=True, deleted_at__isnull=True)

