from __future__ import annotations

from uuid import UUID

from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.coupons.models import Coupon


def get_coupon_by_code(code: str) -> Coupon | None:
    return Coupon.objects.filter(
        code__iexact=code,
        is_active=True,
        deleted_at__isnull=True,
    ).first()


def get_coupon_by_id(coupon_id: str | UUID) -> Coupon | None:
    return Coupon.objects.filter(id=coupon_id, deleted_at__isnull=True).first()


def get_active_coupons() -> QuerySet[Coupon]:
    now = timezone.now()
    return Coupon.objects.filter(
        is_active=True,
        deleted_at__isnull=True,
        valid_from__lte=now,
    ).filter(
        Q(valid_until__isnull=True) | Q(valid_until__gte=now),
    )
