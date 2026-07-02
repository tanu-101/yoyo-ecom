from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.selectors.orders import get_order_by_id
from apps.shipping.services.tracking import create_tracking, update_tracking_status

from .serializers import AdminTrackingSerializer, AdminTrackingUpdateSerializer


class AdminCreateTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AdminTrackingSerializer, responses=dict)
    def post(self, request: Request, order_id: str) -> Response:
        order = get_order_by_id(order_id=order_id)
        if not order:
            return Response(
                {"error": {"code": "not_found", "message": "Order not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminTrackingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tracking = create_tracking(
            order=order,
            carrier=serializer.validated_data["carrier"],
            tracking_number=serializer.validated_data["tracking_number"],
            tracking_url=serializer.validated_data.get("tracking_url", ""),
            estimated_delivery=serializer.validated_data.get("estimated_delivery"),
        )

        return Response(
            {
                "data": {"id": str(tracking.id), "tracking_number": tracking.tracking_number},
                "message": "Tracking created.",
            },
            status=status.HTTP_201_CREATED,
        )


class AdminUpdateTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AdminTrackingUpdateSerializer, responses=dict)
    def patch(self, request: Request, order_id: str) -> Response:
        order = get_order_by_id(order_id=order_id)
        if not order:
            return Response(
                {"error": {"code": "not_found", "message": "Order not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not hasattr(order, "tracking"):
            return Response(
                {"error": {"code": "not_found", "message": "No tracking record for this order."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminTrackingUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tracking = update_tracking_status(
            tracking=order.tracking,
            status=serializer.validated_data["status"],
        )

        return Response(
            {"data": {"status": tracking.status}, "message": "Tracking updated."},
        )
