from __future__ import annotations

import pytest

from apps.carts.selectors.carts import get_cart_for_user, get_cart_items
from apps.catalog.factories import VariantFactory

pytestmark = pytest.mark.django_db


def test_cart_get_creates_empty_cart(api_client, customer_user):
    api_client.force_authenticate(user=customer_user)

    response = api_client.get("/api/v1/customer/cart/")

    assert response.status_code == 200
    assert response.data["data"]["items"] == []
    assert float(response.data["data"]["totals"]["total"]) == 0.00


def test_cart_add_item(api_client, customer_user):
    variant = VariantFactory(stock_quantity=10, price="25.00")
    api_client.force_authenticate(user=customer_user)

    response = api_client.post(
        "/api/v1/customer/cart/items/",
        {"variant_id": str(variant.id), "quantity": 2},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["data"]["quantity"] == 2
    assert float(response.data["data"]["unit_price"]) == 25.00


def test_cart_add_item_accumulates_on_repost(api_client, customer_user):
    variant = VariantFactory(stock_quantity=10)
    api_client.force_authenticate(user=customer_user)

    api_client.post(
        "/api/v1/customer/cart/items/",
        {"variant_id": str(variant.id), "quantity": 2},
        format="json",
    )
    response = api_client.post(
        "/api/v1/customer/cart/items/",
        {"variant_id": str(variant.id), "quantity": 3},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["data"]["quantity"] == 5


def test_cart_add_item_fails_on_insufficient_stock(api_client, customer_user):
    variant = VariantFactory(stock_quantity=1)
    api_client.force_authenticate(user=customer_user)

    response = api_client.post(
        "/api/v1/customer/cart/items/",
        {"variant_id": str(variant.id), "quantity": 5},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"]["code"] == "insufficient_stock"


def test_cart_update_item_quantity(api_client, customer_user):
    variant = VariantFactory(stock_quantity=10)
    api_client.force_authenticate(user=customer_user)

    add_resp = api_client.post(
        "/api/v1/customer/cart/items/",
        {"variant_id": str(variant.id), "quantity": 1},
        format="json",
    )
    item_id = add_resp.data["data"]["id"]

    response = api_client.patch(
        f"/api/v1/customer/cart/items/{item_id}/",
        {"quantity": 4},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["data"]["quantity"] == 4


def test_cart_remove_item(api_client, customer_user):
    variant = VariantFactory(stock_quantity=10)
    api_client.force_authenticate(user=customer_user)

    add_resp = api_client.post(
        "/api/v1/customer/cart/items/",
        {"variant_id": str(variant.id), "quantity": 1},
        format="json",
    )
    item_id = add_resp.data["data"]["id"]

    response = api_client.delete(f"/api/v1/customer/cart/items/{item_id}/")

    assert response.status_code == 204
    cart = get_cart_for_user(user=customer_user)
    assert cart is not None
    assert get_cart_items(cart=cart).count() == 0


def test_cart_clear(api_client, customer_user):
    variant = VariantFactory(stock_quantity=10)
    api_client.force_authenticate(user=customer_user)
    api_client.post(
        "/api/v1/customer/cart/items/",
        {"variant_id": str(variant.id), "quantity": 1},
        format="json",
    )

    response = api_client.delete("/api/v1/customer/cart/")

    assert response.status_code == 204
    cart = get_cart_for_user(user=customer_user)
    assert cart is not None
    assert get_cart_items(cart=cart).count() == 0


def test_cart_requires_authentication(api_client):
    response = api_client.get("/api/v1/customer/cart/")
    assert response.status_code == 401


def test_cart_totals_reflect_items(api_client, customer_user):
    variant = VariantFactory(stock_quantity=10, price="30.00")
    api_client.force_authenticate(user=customer_user)
    api_client.post(
        "/api/v1/customer/cart/items/",
        {"variant_id": str(variant.id), "quantity": 3},
        format="json",
    )

    response = api_client.get("/api/v1/customer/cart/")

    assert response.status_code == 200
    totals = response.data["data"]["totals"]
    assert float(totals["subtotal"]) == pytest.approx(90.00, abs=0.01)
    assert float(totals["total"]) == pytest.approx(90.00, abs=0.01)
