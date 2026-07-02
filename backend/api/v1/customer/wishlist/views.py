from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from apps.common.exceptions import BusinessRuleViolation
from apps.wishlist.selectors.wishlist import get_wishlist_for_customer, get_wishlist_item_by_id
from apps.wishlist.services.wishlist import add_to_wishlist, move_to_cart, remove_from_wishlist

from .serializers import AddWishlistItemSerializer, MoveToCartSerializer, WishlistItemSerializer


class WishlistListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=WishlistItemSerializer(many=True))
    def get(self, request: Request) -> Response:
        items = get_wishlist_for_customer(customer=request.user)
        return Response(
            {"data": WishlistItemSerializer(items, many=True).data, "message": "Success"}
        )

    @extend_schema(request=AddWishlistItemSerializer, responses=WishlistItemSerializer)
    def post(self, request: Request) -> Response:
        serializer = AddWishlistItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = Product.objects.filter(
            id=serializer.validated_data["product"],
            deleted_at__isnull=True,
        ).first()
        if not product:
            return Response(
                {"error": {"code": "not_found", "message": "Product not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        item = add_to_wishlist(
            customer=request.user,
            product=product,
            variant=serializer.validated_data.get("variant"),
            notes=serializer.validated_data.get("notes", ""),
        )

        return Response(
            {"data": WishlistItemSerializer(item).data, "message": "Added to wishlist."},
            status=status.HTTP_201_CREATED,
        )


class WishlistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_item(self, request: Request, item_id: str):
        item = get_wishlist_item_by_id(item_id=item_id)
        if not item or item.customer_id != request.user.id:
            return None
        return item

    @extend_schema(responses={204: None})
    def delete(self, request: Request, item_id: str) -> Response:
        item = self._get_item(request, item_id)
        if not item:
            return Response(
                {"error": {"code": "not_found", "message": "Wishlist item not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        remove_from_wishlist(item=item)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MoveToCartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=MoveToCartSerializer, responses=dict)
    def post(self, request: Request, item_id: str) -> Response:
        item = get_wishlist_item_by_id(item_id=item_id)
        if not item or item.customer_id != request.user.id:
            return Response(
                {"error": {"code": "not_found", "message": "Wishlist item not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MoveToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cart_item = move_to_cart(
                customer=request.user,
                item=item,
                quantity=serializer.validated_data["quantity"],
            )
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from api.v1.customer.cart.serializers import CartItemSerializer

        return Response(
            {"data": CartItemSerializer(cart_item).data, "message": "Moved to cart."},
        )
