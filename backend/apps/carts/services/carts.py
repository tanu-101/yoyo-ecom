from __future__ import annotations

from django.db import transaction

from apps.accounts.models import User
from apps.carts.models.cart import Cart
from apps.carts.models.cart_item import CartItem
from apps.carts.selectors.carts import get_cart_for_user
from apps.catalog.models import Variant
from apps.common.exceptions import BusinessRuleViolation
from apps.inventory.selectors.stock import is_stock_available


def get_or_create_cart(*, user: User) -> Cart:
    """Gets or creates the user's cart."""
    cart, _ = Cart.objects.get_or_create(customer=user)
    return cart


@transaction.atomic
def add_item_to_cart(*, user: User, variant: Variant, quantity: int) -> CartItem:
    """
    Adds a variant to the cart, or updates the quantity if it already exists.
    Validates that requested quantity is available in stock.
    """
    if quantity <= 0:
        raise BusinessRuleViolation("Quantity must be greater than zero.", code="invalid_quantity")

    if variant.deleted_at is not None or variant.status != "active":
        raise BusinessRuleViolation(
            "This product variant is not available.", code="variant_unavailable"
        )

    cart = get_or_create_cart(user=user)

    # Check if item already exists in cart
    existing_item = cart.items.filter(variant=variant).first()
    new_total_qty = (existing_item.quantity + quantity) if existing_item else quantity

    # Validate stock availability for total requested quantity
    if not is_stock_available(variant=variant, quantity=new_total_qty):
        raise BusinessRuleViolation(
            f"Insufficient stock. Only {variant.stock_quantity} units available.",
            code="insufficient_stock",
        )

    if existing_item:
        existing_item.quantity = new_total_qty
        existing_item.unit_price = variant.price  # Refresh price
        existing_item.save(update_fields=["quantity", "unit_price", "updated_at"])
        return existing_item

    return CartItem.objects.create(
        cart=cart,
        product=variant.product,
        variant=variant,
        quantity=quantity,
        unit_price=variant.price,
    )


@transaction.atomic
def update_cart_item_quantity(*, user: User, cart_item: CartItem, quantity: int) -> CartItem:
    """
    Sets the cart item quantity to the given value.
    Validates stock availability for the new quantity.
    """
    if quantity <= 0:
        raise BusinessRuleViolation("Quantity must be greater than zero.", code="invalid_quantity")

    if not is_stock_available(variant=cart_item.variant, quantity=quantity):
        raise BusinessRuleViolation(
            f"Insufficient stock. Only {cart_item.variant.stock_quantity} units available.",
            code="insufficient_stock",
        )

    cart_item.quantity = quantity
    cart_item.unit_price = cart_item.variant.price  # Refresh price
    cart_item.save(update_fields=["quantity", "unit_price", "updated_at"])
    return cart_item


@transaction.atomic
def remove_item_from_cart(*, user: User, cart_item: CartItem) -> None:
    """Removes a single item from the cart."""
    cart = get_cart_for_user(user=user)
    if not cart or cart_item.cart_id != cart.id:
        raise BusinessRuleViolation("Cart item not found.", code="not_found")
    cart_item.delete()


@transaction.atomic
def clear_cart(*, user: User) -> None:
    """Removes all items from the user's cart."""
    cart = get_cart_for_user(user=user)
    if cart:
        cart.items.all().delete()
