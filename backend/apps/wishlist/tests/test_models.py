from __future__ import annotations

import pytest

from apps.wishlist.factories import WishlistItemFactory
from apps.wishlist.models import WishlistItem

pytestmark = pytest.mark.django_db


class TestWishlistItem:
    def test_create_item(self):
        WishlistItemFactory()
        assert WishlistItem.objects.count() == 1
