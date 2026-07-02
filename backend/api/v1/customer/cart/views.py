from __future__ import annotations

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.carts.models.cart_item import CartItem
from apps.carts.selectors.carts import get_cart_for_user
from apps.carts.services.carts import (
    add_item_to_cart,
    clear_cart,
    get_or_create_cart,
    remove_item_from_cart,
    update_cart_item_quantity,
)
from apps.catalog.models import Variant
from apps.common.exceptions import BusinessRuleViolation

from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)


def _error(exc: BusinessRuleViolation, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response({"error": {"code": exc.code, "message": exc.message}}, status=status_code)


class CartView(APIView):
    """
    GET  /api/v1/customer/cart/   — Retrieve current cart with items and totals.
    DELETE /api/v1/customer/cart/ — Clear all items from the cart.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CartSerializer)
    def get(self, request: Request) -> Response:
        cart = get_or_create_cart(user=request.user)
        return Response({"data": CartSerializer(cart).data, "message": "Success"})

    @extend_schema(responses={204: None})
    def delete(self, request: Request) -> Response:
        clear_cart(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemListView(APIView):
    """
    POST /api/v1/customer/cart/items/ — Add an item to the cart.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(request=AddCartItemSerializer, responses=CartItemSerializer)
    def post(self, request: Request) -> Response:
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        variant = get_object_or_404(
            Variant,
            id=serializer.validated_data["variant_id"],
            deleted_at__isnull=True,
        )

        try:
            item = add_item_to_cart(
                user=request.user,
                variant=variant,
                quantity=serializer.validated_data["quantity"],
            )
        except BusinessRuleViolation as exc:
            return _error(exc)

        return Response(
            {"data": CartItemSerializer(item).data, "message": "Item added to cart."},
            status=status.HTTP_201_CREATED,
        )


class CartItemDetailView(APIView):
    """
    PATCH  /api/v1/customer/cart/items/{id}/ — Update item quantity.
    DELETE /api/v1/customer/cart/items/{id}/ — Remove item from cart.
    """

    permission_classes = [IsAuthenticated]

    def _get_item(self, request: Request, item_id: str) -> CartItem:
        """Gets a cart item belonging to the current user's cart."""
        cart = get_cart_for_user(user=request.user)
        return get_object_or_404(CartItem, id=item_id, cart=cart)

    @extend_schema(request=UpdateCartItemSerializer, responses=CartItemSerializer)
    def patch(self, request: Request, item_id: str) -> Response:
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = self._get_item(request, item_id)
        try:
            item = update_cart_item_quantity(
                user=request.user,
                cart_item=item,
                quantity=serializer.validated_data["quantity"],
            )
        except BusinessRuleViolation as exc:
            return _error(exc)

        return Response({"data": CartItemSerializer(item).data, "message": "Cart updated."})

    @extend_schema(responses={204: None})
    def delete(self, request: Request, item_id: str) -> Response:
        item = self._get_item(request, item_id)
        try:
            remove_item_from_cart(user=request.user, cart_item=item)
        except BusinessRuleViolation as exc:
            return _error(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)
