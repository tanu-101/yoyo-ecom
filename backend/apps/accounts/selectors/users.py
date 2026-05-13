from __future__ import annotations

from uuid import UUID

from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.accounts.constants import UserRole
from apps.accounts.models import User, UserOTP


def active_users() -> QuerySet[User]:
    return User.objects.filter(is_active=True, deleted_at__isnull=True)


def users_list(
    *,
    role: str | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    include_deleted: bool = False,
) -> QuerySet[User]:
    queryset = User.objects.all()
    if not include_deleted:
        queryset = queryset.filter(deleted_at__isnull=True)
    if role:
        queryset = queryset.filter(role=role)
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    if search:
        queryset = queryset.filter(
            Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
        )
    return queryset.order_by("email")


def get_user_by_id(user_id: str | UUID, *, include_deleted: bool = False) -> User | None:
    queryset = User.objects.all()
    if not include_deleted:
        queryset = queryset.filter(deleted_at__isnull=True)
    return queryset.filter(id=user_id).first()


def get_active_user_by_email(email: str) -> User | None:
    return active_users().filter(email__iexact=email).first()


def staff_users(*, include_inactive: bool = False) -> QuerySet[User]:
    queryset = users_list(role=UserRole.STAFF)
    if not include_inactive:
        queryset = queryset.filter(is_active=True)
    return queryset


def user_permissions(user: User) -> list[str]:
    if user.is_superuser or user.role == UserRole.ADMIN:
        return ["*"]
    if user.role != UserRole.STAFF:
        return []
    return list(
        user.staff_permissions.filter(is_enabled=True).values_list("permission_code", flat=True)
    )


def is_last_active_admin(user: User) -> bool:
    if not (user.is_superuser or user.role == UserRole.ADMIN):
        return False
    return (
        active_users()
        .filter(Q(role=UserRole.ADMIN) | Q(is_superuser=True))
        .exclude(id=user.id)
        .count()
        == 0
    )


def get_valid_otp(*, user: User, purpose: str, code_hash: str) -> UserOTP | None:
    return (
        UserOTP.objects.filter(
            user=user,
            purpose=purpose,
            code_hash=code_hash,
            consumed_at__isnull=True,
            expires_at__gt=timezone.now(),
        )
        .order_by("-created_at")
        .first()
    )
