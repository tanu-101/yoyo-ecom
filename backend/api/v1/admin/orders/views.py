from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import BusinessRuleViolation
from apps.orders.selectors.orders import get_order_by_id, get_orders_for_admin
from apps.orders.services.cancellation import cancel_order
from apps.orders.services.status_transitions import transition_order_status

from .serializers import (
    AdminCancelOrderSerializer,
    AdminOrderDetailSerializer,
    AdminOrderListSerializer,
    AdminUpdateOrderStatusSerializer,
)


class AdminOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=AdminOrderListSerializer(many=True))
    def get(self, request: Request) -> Response:
        orders = get_orders_for_admin(
            status=request.query_params.get("status"),
            payment_status=request.query_params.get("payment_status"),
            customer=request.query_params.get("customer"),
            date_from=request.query_params.get("date_from"),
            date_to=request.query_params.get("date_to"),
            search=request.query_params.get("search"),
        )

        # Pagination
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        start = (page - 1) * page_size
        end = start + page_size
        total = orders.count()
        total_pages = (total + page_size - 1) // page_size

        return Response(
            {
                "data": AdminOrderListSerializer(orders[start:end], many=True).data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                },
            }
        )


class AdminOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=AdminOrderDetailSerializer)
    def get(self, request: Request, order_id: str) -> Response:
        order = get_order_by_id(order_id=order_id)
        if not order:
            return Response(
                {"error": {"code": "not_found", "message": "Order not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": AdminOrderDetailSerializer(order).data, "message": "Success"})


class AdminUpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AdminUpdateOrderStatusSerializer, responses=AdminOrderDetailSerializer)
    def post(self, request: Request, order_id: str) -> Response:
        order = get_order_by_id(order_id=order_id)
        if not order:
            return Response(
                {"error": {"code": "not_found", "message": "Order not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminUpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = transition_order_status(
                order=order,
                to_status=serializer.validated_data["status"],
                changed_by=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"data": AdminOrderDetailSerializer(order).data, "message": "Status updated."}
        )


class AdminCancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AdminCancelOrderSerializer, responses=AdminOrderDetailSerializer)
    def post(self, request: Request, order_id: str) -> Response:
        order = get_order_by_id(order_id=order_id)
        if not order:
            return Response(
                {"error": {"code": "not_found", "message": "Order not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminCancelOrderSerializer(data=request.data)
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

        return Response(
            {"data": AdminOrderDetailSerializer(order).data, "message": "Order cancelled."}
        )
