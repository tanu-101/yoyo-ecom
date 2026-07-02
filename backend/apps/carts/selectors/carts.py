from __future__ import annotations

from decimal import Decimal

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.carts.models.cart import Cart
from apps.carts.models.cart_item import CartItem


def get_cart_for_user(*, user: User) -> Cart | None:
    """Returns the user's cart or None if it does not exist."""
    try:
        return Cart.objects.select_related("customer").get(customer=user)
    except Cart.DoesNotExist:
        return None


def get_cart_items(*, cart: Cart) -> QuerySet[CartItem]:
    """Returns all items in the cart, prefetching variant and product details."""
    return cart.items.select_related(
        "product",
        "variant",
        "variant__product",
    ).all()


def calculate_cart_totals(*, cart: Cart) -> dict:
    """
    Dynamically calculates cart totals from current item quantities and prices.
    Returns subtotal, discount_amount (placeholder for coupon integration), and total.
    """
    items = get_cart_items(cart=cart)
    subtotal = Decimal("0.00")
    for item in items:
        subtotal += item.unit_price * item.quantity

    discount_amount = Decimal("0.00")  # Coupon integration placeholder
    total = subtotal - discount_amount

    return {
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "total": total,
        "item_count": items.count(),
    }
