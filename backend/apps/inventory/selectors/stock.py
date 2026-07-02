from __future__ import annotations

from django.db.models import Sum
from django.utils import timezone

from apps.catalog.models import Variant
from apps.inventory.constants import StockReservationStatus
from apps.inventory.models.stock_reservation import StockReservation


def get_active_reservations_for_variant(*, variant: Variant) -> int:
    """
    Returns the sum of quantities for all active, unexpired reservations for a variant.
    """
    now = timezone.now()
    result = StockReservation.objects.filter(
        variant=variant,
        status=StockReservationStatus.ACTIVE,
        expires_at__gt=now,
    ).aggregate(total=Sum("quantity"))

    return result["total"] or 0


def get_stock_quantity(*, variant: Variant) -> int:
    """
    Returns the net available stock for a variant (physical stock minus active reservations).
    """
    active_reservations = get_active_reservations_for_variant(variant=variant)
    return max(0, variant.stock_quantity - active_reservations)


def is_stock_available(*, variant: Variant, quantity: int) -> bool:
    """
    Checks if there is enough net available stock for the requested quantity.
    """
    return get_stock_quantity(variant=variant) >= quantity
