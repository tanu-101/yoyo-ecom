from __future__ import annotations

import pytest

from apps.catalog.factories import VariantFactory
from apps.common.exceptions import BusinessRuleViolation
from apps.inventory.constants import InventoryTransactionType
from apps.inventory.selectors.stock import (
    get_active_reservations_for_variant,
    get_stock_quantity,
    is_stock_available,
)
from apps.inventory.services.stock_adjustments import adjust_stock
from apps.inventory.services.stock_locks import release_reservation, reserve_stock

pytestmark = pytest.mark.django_db


def test_adjust_stock_increases_quantity():
    variant = VariantFactory(stock_quantity=10)

    txn = adjust_stock(
        variant=variant,
        quantity_changed=5,
        transaction_type=InventoryTransactionType.MANUAL_ADJUSTMENT,
    )

    variant.refresh_from_db()
    assert variant.stock_quantity == 15
    assert txn.stock_before == 10
    assert txn.stock_after == 15
    assert txn.quantity_changed == 5


def test_adjust_stock_decreases_quantity():
    variant = VariantFactory(stock_quantity=10)

    txn = adjust_stock(
        variant=variant,
        quantity_changed=-3,
        transaction_type=InventoryTransactionType.MANUAL_ADJUSTMENT,
    )

    variant.refresh_from_db()
    assert variant.stock_quantity == 7
    assert txn.stock_after == 7


def test_adjust_stock_raises_on_negative_result():
    variant = VariantFactory(stock_quantity=2)

    with pytest.raises(BusinessRuleViolation, match="Insufficient stock"):
        adjust_stock(
            variant=variant,
            quantity_changed=-5,
            transaction_type=InventoryTransactionType.MANUAL_ADJUSTMENT,
        )

    # stock_quantity must be unchanged after failed transaction
    variant.refresh_from_db()
    assert variant.stock_quantity == 2


def test_is_stock_available_true():
    variant = VariantFactory(stock_quantity=10)
    assert is_stock_available(variant=variant, quantity=5) is True


def test_is_stock_available_false():
    variant = VariantFactory(stock_quantity=2)
    assert is_stock_available(variant=variant, quantity=5) is False


def test_reserve_stock_creates_reservation(customer_user):
    variant = VariantFactory(stock_quantity=10)

    reservation = reserve_stock(variant=variant, user=customer_user, quantity=3)

    assert reservation.quantity == 3
    assert reservation.status == "active"
    # Net available stock should account for reservation
    assert get_stock_quantity(variant=variant) == 7


def test_reserve_stock_raises_on_insufficient_stock(customer_user):
    variant = VariantFactory(stock_quantity=2)

    with pytest.raises(BusinessRuleViolation, match="Insufficient available stock"):
        reserve_stock(variant=variant, user=customer_user, quantity=5)


def test_get_active_reservations_counts_correctly(customer_user):
    variant = VariantFactory(stock_quantity=20)

    reserve_stock(variant=variant, user=customer_user, quantity=3)
    reserve_stock(variant=variant, user=customer_user, quantity=4)

    total_reserved = get_active_reservations_for_variant(variant=variant)
    assert total_reserved == 7


def test_release_reservation(customer_user):
    variant = VariantFactory(stock_quantity=10)
    reservation = reserve_stock(variant=variant, user=customer_user, quantity=3)

    release_reservation(reservation=reservation)

    reservation.refresh_from_db()
    assert reservation.status == "released"
    # After release, net available should be back to full stock
    assert get_stock_quantity(variant=variant) == 10


def test_release_non_active_reservation_raises(customer_user):
    variant = VariantFactory(stock_quantity=10)
    reservation = reserve_stock(variant=variant, user=customer_user, quantity=3)
    release_reservation(reservation=reservation)

    with pytest.raises(BusinessRuleViolation, match="Only active reservations can be released"):
        release_reservation(reservation=reservation)
