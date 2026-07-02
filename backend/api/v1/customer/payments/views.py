from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import BusinessRuleViolation
from apps.orders.selectors.orders import get_order_for_customer
from apps.payments.selectors.payments import get_payment_by_id, get_payments_for_customer
from apps.payments.services.stripe_payment_intents import create_payment_intent

from .serializers import CreatePaymentIntentSerializer, PaymentSerializer


class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CreatePaymentIntentSerializer, responses=PaymentSerializer)
    def post(self, request: Request) -> Response:
        serializer = CreatePaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_order_for_customer(
            customer=request.user,
            order_id=serializer.validated_data["order"],
        )
        if not order:
            return Response(
                {"error": {"code": "not_found", "message": "Order not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            result = create_payment_intent(order=order, customer=request.user)
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"data": result, "message": "Payment intent created."})


class CustomerPaymentListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=PaymentSerializer(many=True))
    def get(self, request: Request) -> Response:
        payments = get_payments_for_customer(customer=request.user)
        return Response({"data": PaymentSerializer(payments, many=True).data, "message": "Success"})


class CustomerPaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=PaymentSerializer)
    def get(self, request: Request, payment_id: str) -> Response:
        payment = get_payment_by_id(payment_id=payment_id)
        if not payment or payment.order.customer_id != request.user.id:
            return Response(
                {"error": {"code": "not_found", "message": "Payment not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": PaymentSerializer(payment).data, "message": "Success"})
