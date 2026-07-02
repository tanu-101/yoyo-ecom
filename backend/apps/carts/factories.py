from __future__ import annotations

import factory

from apps.accounts.factories import CustomerUserFactory
from apps.carts.models.cart import Cart
from apps.carts.models.cart_item import CartItem
from apps.catalog.factories import CategoryFactory, ProductFactory, VariantFactory

__all__ = [
    "CartFactory",
    "CartItemFactory",
    "CategoryFactory",
    "ProductFactory",
    "VariantFactory",
]


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart
        django_get_or_create = ("customer",)

    customer = factory.SubFactory(CustomerUserFactory)


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    variant = factory.SubFactory(VariantFactory)
    quantity = 1
    unit_price = factory.LazyFunction(lambda: "99.99")
