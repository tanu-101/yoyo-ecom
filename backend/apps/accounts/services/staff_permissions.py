from __future__ import annotations

from django.utils import timezone

from apps.accounts.constants import UserRole
from apps.accounts.models import StaffPermission, User
from apps.common.exceptions import BusinessRuleViolation


def set_staff_permission(
    *,
    staff_user: User,
    permission_code: str,
    is_enabled: bool,
    granted_by: User | None = None,
) -> StaffPermission:
    if staff_user.role != UserRole.STAFF:
        raise BusinessRuleViolation("Permissions can only be assigned to staff users.")

    permission, _ = StaffPermission.objects.update_or_create(
        user=staff_user,
        permission_code=permission_code,
        defaults={
            "is_enabled": is_enabled,
            "granted_by": granted_by,
            "granted_at": timezone.now() if is_enabled else None,
        },
    )
    return permission
