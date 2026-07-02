from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.shipping.models import ShippingMethod


def get_active_shipping_methods() -> QuerySet[ShippingMethod]:
    return ShippingMethod.objects.filter(is_active=True)


def get_shipping_method_by_id(method_id: str | UUID) -> ShippingMethod | None:
    return ShippingMethod.objects.filter(id=method_id, is_active=True).first()
