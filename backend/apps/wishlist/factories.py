from __future__ import annotations

import factory

from apps.accounts.factories import CustomerUserFactory
from apps.catalog.factories import ProductFactory
from apps.wishlist.models import WishlistItem


class WishlistItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WishlistItem

    customer = factory.SubFactory(CustomerUserFactory)
    product = factory.SubFactory(ProductFactory)
