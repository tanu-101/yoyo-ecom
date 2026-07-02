from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.wishlist.models import WishlistItem


def get_wishlist_for_customer(*, customer: User) -> QuerySet[WishlistItem]:
    return WishlistItem.objects.filter(customer=customer).select_related("product", "variant")


def get_wishlist_item_by_id(item_id: str | UUID) -> WishlistItem | None:
    return WishlistItem.objects.select_related("product", "variant").filter(id=item_id).first()
