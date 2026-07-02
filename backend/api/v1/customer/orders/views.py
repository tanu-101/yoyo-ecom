from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import BusinessRuleViolation
from apps.orders.selectors.orders import get_order_for_customer, get_orders_for_customer
from apps.orders.services.cancellation import cancel_order
from apps.orders.services.checkout import create_order_from_cart

from .serializers import CancelOrderSerializer, CheckoutSerializer, OrderSerializer


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CheckoutSerializer, responses=OrderSerializer)
    def post(self, request: Request) -> Response:
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = create_order_from_cart(
                customer=request.user,
                shipping_cost=serializer.validated_data.get("shipping_cost", 0),
                tax_amount=serializer.validated_data.get("tax_amount", 0),
                customer_notes=serializer.validated_data.get("customer_notes", ""),
            )
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"data": OrderSerializer(order).data, "message": "Order created."},
            status=status.HTTP_201_CREATED,
        )


class CustomerOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=OrderSerializer(many=True))
    def get(self, request: Request) -> Response:
        orders = get_orders_for_customer(
            customer=request.user,
            status=request.query_params.get("status"),
            payment_status=request.query_params.get("payment_status"),
            date_from=request.query_params.get("date_from"),
            date_to=request.query_params.get("date_to"),
        )
        return Response({"data": OrderSerializer(orders, many=True).data, "message": "Success"})


class CustomerOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=OrderSerializer)
    def get(self, request: Request, order_id: str) -> Response:
        order = get_order_for_customer(customer=request.user, order_id=order_id)
        if not order:
            return Response(
                {"error": {"code": "not_found", "message": "Order not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": OrderSerializer(order).data, "message": "Success"})


class CustomerCancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CancelOrderSerializer, responses=OrderSerializer)
    def post(self, request: Request, order_id: str) -> Response:
        order = get_order_for_customer(customer=request.user, order_id=order_id)
        if not order:
            return Response(
                {"error": {"code": "not_found", "message": "Order not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CancelOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = cancel_order(
                order=order,
                cancelled_by=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"data": OrderSerializer(order).data, "message": "Order cancelled."})
