from __future__ import annotations

import pytest

from apps.catalog.factories import ProductFactory, VariantFactory
from apps.common.exceptions import BusinessRuleViolation
from apps.wishlist.factories import WishlistItemFactory
from apps.wishlist.models import WishlistItem
from apps.wishlist.services.wishlist import add_to_wishlist, move_to_cart, remove_from_wishlist

pytestmark = pytest.mark.django_db


class TestAddToWishlist:
    def test_adds_item(self, customer_user):
        product = ProductFactory()
        variant = VariantFactory(product=product)

        item = add_to_wishlist(
            customer=customer_user,
            product=product,
            variant=variant,
            notes="Want this!",
        )

        assert item.customer == customer_user
        assert item.product == product
        assert item.variant == variant
        assert item.notes == "Want this!"
        assert WishlistItem.objects.filter(customer=customer_user).count() == 1

    def test_adds_item_without_variant(self, customer_user):
        product = ProductFactory()

        item = add_to_wishlist(customer=customer_user, product=product)

        assert item.product == product
        assert item.variant is None

    def test_returns_existing_item(self, customer_user):
        product = ProductFactory()
        existing = WishlistItemFactory(customer=customer_user, product=product)

        item = add_to_wishlist(customer=customer_user, product=product)

        assert item.id == existing.id
        assert WishlistItem.objects.filter(customer=customer_user).count() == 1


class TestRemoveFromWishlist:
    def test_removes_item(self, customer_user):
        item = WishlistItemFactory(customer=customer_user)

        remove_from_wishlist(item=item)

        assert WishlistItem.objects.filter(id=item.id).count() == 0


class TestMoveToCart:
    def test_moves_item_to_cart_with_variant(self, customer_user):
        product = ProductFactory()
        variant = VariantFactory(product=product, stock_quantity=10)
        item = WishlistItemFactory(customer=customer_user, product=product, variant=variant)

        cart_item = move_to_cart(customer=customer_user, item=item, quantity=2)

        assert cart_item.variant == variant
        assert cart_item.quantity == 2
        assert WishlistItem.objects.filter(id=item.id).count() == 0

    def test_moves_item_to_cart_with_product_active_variant(self, customer_user):
        product = ProductFactory()
        VariantFactory(product=product, stock_quantity=10)
        item = WishlistItemFactory(customer=customer_user, product=product, variant=None)

        cart_item = move_to_cart(customer=customer_user, item=item)

        assert cart_item.variant is not None
        assert WishlistItem.objects.filter(id=item.id).count() == 0

    def test_raises_on_no_active_variant(self, customer_user):
        product = ProductFactory()
        item = WishlistItemFactory(customer=customer_user, product=product, variant=None)

        with pytest.raises(BusinessRuleViolation) as exc:
            move_to_cart(customer=customer_user, item=item)

        assert exc.value.code == "variant_unavailable"
