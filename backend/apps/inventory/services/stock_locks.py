from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from apps.catalog.models import Variant
from apps.common.exceptions import BusinessRuleViolation
from apps.inventory.constants import InventoryTransactionType, StockReservationStatus
from apps.inventory.models.stock_reservation import StockReservation
from apps.inventory.selectors.stock import is_stock_available
from apps.inventory.services.stock_adjustments import adjust_stock

if TYPE_CHECKING:
    from apps.accounts.models import User
    from apps.orders.models.order import Order


@transaction.atomic
def reserve_stock(
    *,
    variant: Variant,
    user: User,
    quantity: int,
    expires_in_minutes: int = 15,
) -> StockReservation:
    """
    Reserves stock for a customer inside an atomic transaction.
    """
    # Write-lock the Variant record during calculation
    locked_variant = Variant.objects.select_for_update().get(id=variant.id)

    if quantity <= 0:
        raise BusinessRuleViolation(
            "Reservation quantity must be greater than zero.",
            code="invalid_quantity",
        )

    if not is_stock_available(variant=locked_variant, quantity=quantity):
        raise BusinessRuleViolation(
            f"Cannot reserve stock. Insufficient available stock for "
            f"variant '{locked_variant.sku}'.",
            code="insufficient_stock",
        )

    expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)

    return StockReservation.objects.create(
        variant=locked_variant,
        user=user,
        quantity=quantity,
        status=StockReservationStatus.ACTIVE,
        expires_at=expires_at,
    )


@transaction.atomic
def release_reservation(*, reservation: StockReservation) -> None:
    """
    Releases an active stock reservation back to general stock.
    """
    if reservation.status != StockReservationStatus.ACTIVE:
        raise BusinessRuleViolation(
            "Only active reservations can be released.",
            code="invalid_reservation_status",
        )

    reservation.status = StockReservationStatus.RELEASED
    reservation.save(update_fields=["status"])


@transaction.atomic
def consume_reservation(*, reservation: StockReservation, order: Order) -> None:
    """
    Consumes an active stock reservation when an order is successfully completed/placed.
    Triggers physical stock deduction.
    """
    if reservation.status != StockReservationStatus.ACTIVE:
        raise BusinessRuleViolation(
            "Only active reservations can be consumed.",
            code="invalid_reservation_status",
        )

    now = timezone.now()
    if reservation.expires_at <= now:
        reservation.status = StockReservationStatus.EXPIRED
        reservation.save(update_fields=["status"])
        raise BusinessRuleViolation(
            "Cannot consume reservation because it has expired.",
            code="expired_reservation",
        )

    reservation.status = StockReservationStatus.CONSUMED
    reservation.order = order
    reservation.save(update_fields=["status", "order"])

    # Physically deduct the stock from the variant
    adjust_stock(
        variant=reservation.variant,
        quantity_changed=-reservation.quantity,
        transaction_type=InventoryTransactionType.ORDER_PLACED,
        reference_type="order",
        reference_id=order.id,
        created_by=reservation.user,
    )
