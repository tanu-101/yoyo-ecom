from __future__ import annotations

from django.db import transaction

from apps.accounts.models import User
from apps.carts.services.carts import add_item_to_cart
from apps.catalog.models import Product, Variant
from apps.common.exceptions import BusinessRuleViolation
from apps.wishlist.models import WishlistItem


@transaction.atomic
def add_to_wishlist(
    *,
    customer: User,
    product: Product,
    variant: Variant | None = None,
    notes: str = "",
) -> WishlistItem:
    existing = WishlistItem.objects.filter(
        customer=customer,
        product=product,
        variant=variant,
    ).first()

    if existing:
        return existing

    return WishlistItem.objects.create(
        customer=customer,
        product=product,
        variant=variant,
        notes=notes,
    )


@transaction.atomic
def remove_from_wishlist(*, item: WishlistItem) -> None:
    item.delete()


@transaction.atomic
def move_to_cart(
    *,
    customer: User,
    item: WishlistItem,
    quantity: int = 1,
):
    variant = item.variant or item.product.variants.filter(status="active").first()
    if not variant:
        raise BusinessRuleViolation(
            "No active variant found for this product.",
            code="variant_unavailable",
        )

    cart_item = add_item_to_cart(
        user=customer,
        variant=variant,
        quantity=quantity,
    )
    item.delete()

    return cart_item
