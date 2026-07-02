from __future__ import annotations

import pytest

from apps.accounts.factories import CustomerUserFactory
from apps.carts.selectors.carts import calculate_cart_totals, get_cart_for_user, get_cart_items
from apps.carts.services.carts import (
    add_item_to_cart,
    clear_cart,
    get_or_create_cart,
    remove_item_from_cart,
    update_cart_item_quantity,
)
from apps.catalog.factories import VariantFactory
from apps.common.exceptions import BusinessRuleViolation


@pytest.mark.django_db
def test_get_or_create_cart_creates_once():
    user = CustomerUserFactory()
    cart1 = get_or_create_cart(user=user)
    cart2 = get_or_create_cart(user=user)
    assert cart1.id == cart2.id, "get_or_create_cart must return the same cart on successive calls."


@pytest.mark.django_db
def test_add_item_to_cart_creates_cart_item():
    user = CustomerUserFactory()
    variant = VariantFactory(stock_quantity=5)

    item = add_item_to_cart(user=user, variant=variant, quantity=2)

    assert item.quantity == 2
    assert item.unit_price == variant.price
    assert item.variant == variant


@pytest.mark.django_db
def test_add_item_to_cart_accumulates_quantity():
    user = CustomerUserFactory()
    variant = VariantFactory(stock_quantity=10)

    add_item_to_cart(user=user, variant=variant, quantity=2)
    item = add_item_to_cart(user=user, variant=variant, quantity=3)

    assert item.quantity == 5, "Re-adding same variant should accumulate quantity."


@pytest.mark.django_db
def test_add_item_to_cart_raises_on_insufficient_stock():
    user = CustomerUserFactory()
    variant = VariantFactory(stock_quantity=2)

    with pytest.raises(BusinessRuleViolation, match="Insufficient stock"):
        add_item_to_cart(user=user, variant=variant, quantity=5)


@pytest.mark.django_db
def test_add_item_raises_on_zero_quantity():
    user = CustomerUserFactory()
    variant = VariantFactory(stock_quantity=10)

    with pytest.raises(BusinessRuleViolation, match="Quantity must be greater than zero"):
        add_item_to_cart(user=user, variant=variant, quantity=0)


@pytest.mark.django_db
def test_update_cart_item_quantity():
    user = CustomerUserFactory()
    variant = VariantFactory(stock_quantity=10)
    item = add_item_to_cart(user=user, variant=variant, quantity=1)

    updated = update_cart_item_quantity(user=user, cart_item=item, quantity=4)

    assert updated.quantity == 4


@pytest.mark.django_db
def test_update_cart_item_quantity_raises_on_insufficient_stock():
    user = CustomerUserFactory()
    variant = VariantFactory(stock_quantity=3)
    item = add_item_to_cart(user=user, variant=variant, quantity=1)

    with pytest.raises(BusinessRuleViolation, match="Insufficient stock"):
        update_cart_item_quantity(user=user, cart_item=item, quantity=10)


@pytest.mark.django_db
def test_remove_item_from_cart():
    user = CustomerUserFactory()
    variant = VariantFactory(stock_quantity=10)
    item = add_item_to_cart(user=user, variant=variant, quantity=2)
    cart = get_cart_for_user(user=user)
    assert cart is not None

    remove_item_from_cart(user=user, cart_item=item)

    assert get_cart_items(cart=cart).count() == 0


@pytest.mark.django_db
def test_clear_cart():
    user = CustomerUserFactory()
    variant1 = VariantFactory(stock_quantity=10)
    variant2 = VariantFactory(stock_quantity=10)
    add_item_to_cart(user=user, variant=variant1, quantity=1)
    add_item_to_cart(user=user, variant=variant2, quantity=1)

    clear_cart(user=user)

    cart = get_cart_for_user(user=user)
    assert cart is not None
    assert get_cart_items(cart=cart).count() == 0


@pytest.mark.django_db
def test_calculate_cart_totals():
    user = CustomerUserFactory()
    variant = VariantFactory(stock_quantity=10, price="50.00")
    add_item_to_cart(user=user, variant=variant, quantity=3)

    cart = get_cart_for_user(user=user)
    assert cart is not None
    totals = calculate_cart_totals(cart=cart)

    assert totals["subtotal"] == pytest.approx(150.00, abs=0.01)
    assert totals["discount_amount"] == pytest.approx(0.00, abs=0.01)
    assert totals["total"] == pytest.approx(150.00, abs=0.01)
    assert totals["item_count"] == 1
