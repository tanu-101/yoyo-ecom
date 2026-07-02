from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import BusinessRuleViolation
from apps.returns.selectors.returns import get_return_by_id, get_returns_for_admin
from apps.returns.services.approval import approve_return, reject_return
from apps.returns.services.processing import mark_received, process_return

from .serializers import AdminApproveReturnSerializer, AdminRejectReturnSerializer


class AdminReturnListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="v1_admin_returns_list", responses=dict)
    def get(self, request: Request) -> Response:
        returns = get_returns_for_admin()
        from api.v1.customer.returns.serializers import ReturnRequestSerializer

        return Response(
            {"data": ReturnRequestSerializer(returns, many=True).data, "message": "Success"}
        )


class AdminReturnDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request: Request, return_id: str) -> Response:
        ret = get_return_by_id(return_id=return_id)
        if not ret:
            return Response(
                {"error": {"code": "not_found", "message": "Return not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        from api.v1.customer.returns.serializers import ReturnRequestSerializer

        return Response({"data": ReturnRequestSerializer(ret).data, "message": "Success"})


class AdminApproveReturnView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AdminApproveReturnSerializer, responses=dict)
    def post(self, request: Request, return_id: str) -> Response:
        ret = get_return_by_id(return_id=return_id)
        if not ret:
            return Response(
                {"error": {"code": "not_found", "message": "Return not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminApproveReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ret = approve_return(
                return_request=ret,
                reviewed_by=request.user,
                resolution=serializer.validated_data["resolution"],
                refund_amount=serializer.validated_data.get("refund_amount"),
                admin_notes=serializer.validated_data.get("admin_notes", ""),
            )
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from api.v1.customer.returns.serializers import ReturnRequestSerializer

        return Response({"data": ReturnRequestSerializer(ret).data, "message": "Return approved."})


class AdminRejectReturnView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AdminRejectReturnSerializer, responses=dict)
    def post(self, request: Request, return_id: str) -> Response:
        ret = get_return_by_id(return_id=return_id)
        if not ret:
            return Response(
                {"error": {"code": "not_found", "message": "Return not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminRejectReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ret = reject_return(
                return_request=ret,
                reviewed_by=request.user,
                rejection_reason=serializer.validated_data["rejection_reason"],
                admin_notes=serializer.validated_data.get("admin_notes", ""),
            )
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from api.v1.customer.returns.serializers import ReturnRequestSerializer

        return Response({"data": ReturnRequestSerializer(ret).data, "message": "Return rejected."})


class AdminMarkReceivedView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=dict)
    def post(self, request: Request, return_id: str) -> Response:
        ret = get_return_by_id(return_id=return_id)
        if not ret:
            return Response(
                {"error": {"code": "not_found", "message": "Return not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            ret = mark_received(return_request=ret)
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from api.v1.customer.returns.serializers import ReturnRequestSerializer

        return Response(
            {"data": ReturnRequestSerializer(ret).data, "message": "Return marked as received."}
        )


class AdminProcessReturnView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=dict)
    def post(self, request: Request, return_id: str) -> Response:
        ret = get_return_by_id(return_id=return_id)
        if not ret:
            return Response(
                {"error": {"code": "not_found", "message": "Return not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            ret = process_return(return_request=ret, processed_by=request.user)
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from api.v1.customer.returns.serializers import ReturnRequestSerializer

        return Response({"data": ReturnRequestSerializer(ret).data, "message": "Return processed."})
