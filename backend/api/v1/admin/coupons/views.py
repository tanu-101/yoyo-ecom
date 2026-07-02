from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.coupons.models import Coupon
from apps.coupons.selectors.coupons import get_coupon_by_id

from .serializers import CouponCreateSerializer, CouponSerializer


class AdminCouponListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CouponSerializer(many=True))
    def get(self, request: Request) -> Response:
        coupons = Coupon.objects.filter(deleted_at__isnull=True).order_by("-created_at")
        return Response({"data": CouponSerializer(coupons, many=True).data, "message": "Success"})

    @extend_schema(request=CouponCreateSerializer, responses=CouponSerializer)
    def post(self, request: Request) -> Response:
        serializer = CouponCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        coupon = Coupon.objects.create(**serializer.validated_data)
        return Response(
            {"data": CouponSerializer(coupon).data, "message": "Coupon created."},
            status=status.HTTP_201_CREATED,
        )


class AdminCouponDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CouponSerializer)
    def get(self, request: Request, coupon_id: str) -> Response:
        coupon = get_coupon_by_id(coupon_id=coupon_id)
        if not coupon:
            return Response(
                {"error": {"code": "not_found", "message": "Coupon not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": CouponSerializer(coupon).data, "message": "Success"})

    @extend_schema(request=CouponCreateSerializer, responses=CouponSerializer)
    def patch(self, request: Request, coupon_id: str) -> Response:
        coupon = get_coupon_by_id(coupon_id=coupon_id)
        if not coupon:
            return Response(
                {"error": {"code": "not_found", "message": "Coupon not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CouponCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(coupon, field, value)
        coupon.save(update_fields=serializer.validated_data.keys())

        return Response({"data": CouponSerializer(coupon).data, "message": "Coupon updated."})

    @extend_schema(responses={204: None})
    def delete(self, request: Request, coupon_id: str) -> Response:
        coupon = get_coupon_by_id(coupon_id=coupon_id)
        if not coupon:
            return Response(
                {"error": {"code": "not_found", "message": "Coupon not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        coupon.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
