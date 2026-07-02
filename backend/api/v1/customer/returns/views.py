from __future__ import annotations

from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import BusinessRuleViolation
from apps.orders.selectors.orders import get_order_for_customer
from apps.returns.models import ReturnImage, ReturnRequest
from apps.returns.selectors.returns import get_return_by_id, get_returns_for_customer
from apps.returns.services.eligibility import validate_return_eligibility, validate_return_quantity

from .serializers import CreateReturnSerializer, ReturnRequestSerializer


def _generate_return_number() -> str:
    from django.utils import timezone

    year = timezone.now().year
    last = ReturnRequest.objects.select_for_update().order_by("-created_at").first()
    if last and last.return_number:
        last_num = int(last.return_number.split("-")[-1])
        next_num = last_num + 1
    else:
        next_num = 1
    return f"RET-{year}-{next_num:06d}"


class CreateReturnView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CreateReturnSerializer, responses=ReturnRequestSerializer)
    def post(self, request: Request) -> Response:
        serializer = CreateReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_order_for_customer(
            customer=request.user, order_id=serializer.validated_data["order"]
        )
        if not order:
            return Response(
                {"error": {"code": "not_found", "message": "Order not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            validate_return_eligibility(customer=request.user, order=order)
            validate_return_quantity(order=order, items_data=serializer.validated_data["items"])
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            return_request = ReturnRequest.objects.create(
                return_number=_generate_return_number(),
                order=order,
                customer=request.user,
                reason=serializer.validated_data["reason"],
                resolution=serializer.validated_data.get("resolution", ""),
                comments=serializer.validated_data.get("comments", ""),
            )

            for item_data in serializer.validated_data["items"]:
                return_request.items.create(
                    order_item_id=item_data["order_item"],
                    quantity=item_data["quantity"],
                    reason=item_data.get("reason", serializer.validated_data["reason"]),
                    condition_notes=item_data.get("condition_notes", ""),
                )

            for image_url in serializer.validated_data.get("images", []):
                ReturnImage.objects.create(
                    return_request=return_request,
                    image=image_url,
                )

        return Response(
            {
                "data": ReturnRequestSerializer(return_request).data,
                "message": "Return request created.",
            },
            status=status.HTTP_201_CREATED,
        )


class CustomerReturnListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=ReturnRequestSerializer(many=True))
    def get(self, request: Request) -> Response:
        returns = get_returns_for_customer(customer=request.user)
        return Response(
            {"data": ReturnRequestSerializer(returns, many=True).data, "message": "Success"}
        )


class CustomerReturnDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=ReturnRequestSerializer)
    def get(self, request: Request, return_id: str) -> Response:
        ret = get_return_by_id(return_id=return_id)
        if not ret or ret.customer_id != request.user.id:
            return Response(
                {"error": {"code": "not_found", "message": "Return not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": ReturnRequestSerializer(ret).data, "message": "Success"})
