from __future__ import annotations

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Variant
from apps.common.exceptions import BusinessRuleViolation
from apps.common.permissions import IsAdminOrStaffWithPermission
from apps.inventory.constants import InventoryTransactionType
from apps.inventory.models.inventory_transaction import InventoryTransaction
from apps.inventory.models.stock_reservation import StockReservation
from apps.inventory.selectors.stock import (
    get_active_reservations_for_variant,
    get_stock_quantity,
)
from apps.inventory.services.stock_adjustments import adjust_stock

from .serializers import (
    InventoryTransactionSerializer,
    StockAdjustmentSerializer,
    StockReservationSerializer,
    VariantStockSummarySerializer,
)


def _error(
    message: str, code: str = "error", status_code: int = status.HTTP_400_BAD_REQUEST
) -> Response:
    return Response({"error": {"code": code, "message": message}}, status=status_code)


class VariantStockSummaryView(APIView):
    """
    GET /api/v1/admin/inventory/variants/{variant_id}/stock/
    Returns physical stock, active reservations, and net available quantity.
    """

    permission_classes = [IsAdminOrStaffWithPermission]
    required_staff_permission = "inventory.view"

    @extend_schema(responses=VariantStockSummarySerializer)
    def get(self, request: Request, variant_id: str) -> Response:
        variant = get_object_or_404(Variant, id=variant_id, deleted_at__isnull=True)
        active_reservations = get_active_reservations_for_variant(variant=variant)
        net_available = get_stock_quantity(variant=variant)
        data = VariantStockSummarySerializer(
            {
                "variant_id": variant.id,
                "sku": variant.sku,
                "physical_stock": variant.stock_quantity,
                "active_reservations": active_reservations,
                "net_available": net_available,
            }
        ).data
        return Response({"data": data, "message": "Success"})


class StockAdjustmentView(APIView):
    """
    POST /api/v1/admin/inventory/adjustments/
    Manually adjust stock for a variant (add or remove).
    """

    permission_classes = [IsAdminOrStaffWithPermission]
    required_staff_permission = "inventory.view"

    @extend_schema(request=StockAdjustmentSerializer, responses=InventoryTransactionSerializer)
    def post(self, request: Request) -> Response:
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        variant = get_object_or_404(
            Variant,
            id=serializer.validated_data["variant_id"],
            deleted_at__isnull=True,
        )
        try:
            txn = adjust_stock(
                variant=variant,
                quantity_changed=serializer.validated_data["quantity_changed"],
                transaction_type=InventoryTransactionType.MANUAL_ADJUSTMENT,
                notes=serializer.validated_data.get("notes", ""),
                created_by=request.user,
            )
        except BusinessRuleViolation as exc:
            return _error(exc.message, exc.code)

        return Response(
            {"data": InventoryTransactionSerializer(txn).data, "message": "Stock adjusted."},
            status=status.HTTP_201_CREATED,
        )


class InventoryTransactionListView(APIView):
    """
    GET /api/v1/admin/inventory/variants/{variant_id}/transactions/
    Returns the full audit log of stock changes for a variant.
    """

    permission_classes = [IsAdminOrStaffWithPermission]
    required_staff_permission = "inventory.view"

    @extend_schema(responses=InventoryTransactionSerializer(many=True))
    def get(self, request: Request, variant_id: str) -> Response:
        variant = get_object_or_404(Variant, id=variant_id, deleted_at__isnull=True)
        txns = InventoryTransaction.objects.filter(variant=variant).order_by("-created_at")
        return Response(
            {"data": InventoryTransactionSerializer(txns, many=True).data, "message": "Success"}
        )


class StockReservationListView(APIView):
    """
    GET /api/v1/admin/inventory/reservations/
    Returns all active stock reservations (for admin visibility).
    """

    permission_classes = [IsAdminOrStaffWithPermission]
    required_staff_permission = "inventory.view"

    @extend_schema(responses=StockReservationSerializer(many=True))
    def get(self, request: Request) -> Response:
        reservations = StockReservation.objects.select_related("variant", "user", "order").order_by(
            "-created_at"
        )
        return Response(
            {"data": StockReservationSerializer(reservations, many=True).data, "message": "Success"}
        )
