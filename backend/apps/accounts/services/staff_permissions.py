from __future__ import annotations

from django.utils import timezone

from apps.accounts.constants import StaffPermissionCode, UserRole
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


def set_staff_permissions(
    *,
    staff_user: User,
    permission_updates: list[dict],
    granted_by: User | None = None,
) -> list[StaffPermission]:
    permissions: list[StaffPermission] = []
    valid_codes = set(StaffPermissionCode.values)
    for update in permission_updates:
        code = update.get("code")
        if code not in valid_codes:
            raise BusinessRuleViolation("Invalid staff permission code.", code="invalid_permission")
        permissions.append(
            set_staff_permission(
                staff_user=staff_user,
                permission_code=code,
                is_enabled=bool(update.get("is_enabled", True)),
                granted_by=granted_by,
            )
        )
    return permissions


def enabled_permission_codes(staff_user: User) -> list[str]:
    if staff_user.role != UserRole.STAFF:
        return []
    return list(
        staff_user.staff_permissions.filter(is_enabled=True).values_list(
            "permission_code", flat=True
        )
    )
