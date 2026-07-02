from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import BusinessRuleViolation
from apps.payments.selectors.payments import get_payment_by_id, get_payments_for_admin
from apps.payments.services.refunds import process_refund

from .serializers import AdminPaymentSerializer, AdminRefundSerializer


class AdminPaymentListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=AdminPaymentSerializer(many=True))
    def get(self, request: Request) -> Response:
        payments = get_payments_for_admin()
        return Response(
            {"data": AdminPaymentSerializer(payments, many=True).data, "message": "Success"}
        )


class AdminPaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=AdminPaymentSerializer)
    def get(self, request: Request, payment_id: str) -> Response:
        payment = get_payment_by_id(payment_id=payment_id)
        if not payment:
            return Response(
                {"error": {"code": "not_found", "message": "Payment not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": AdminPaymentSerializer(payment).data, "message": "Success"})


class AdminRefundView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AdminRefundSerializer, responses=AdminPaymentSerializer)
    def post(self, request: Request, payment_id: str) -> Response:
        payment = get_payment_by_id(payment_id=payment_id)
        if not payment:
            return Response(
                {"error": {"code": "not_found", "message": "Payment not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refund = process_refund(
                payment=payment,
                amount=serializer.validated_data["amount"],
                reason=serializer.validated_data.get("reason", ""),
                created_by=request.user,
            )
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "data": {"refund": str(refund.id), "amount": str(refund.amount)},
                "message": "Refund processed.",
            },
        )
