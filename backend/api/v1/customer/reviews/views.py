from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import OrderItem
from apps.reviews.models import Review, ReviewImage
from apps.reviews.selectors.reviews import get_review_by_id

from .serializers import CreateReviewSerializer, ReviewSerializer


class CreateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CreateReviewSerializer, responses=ReviewSerializer)
    def post(self, request: Request) -> Response:
        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_item = (
            OrderItem.objects.filter(
                id=serializer.validated_data["order_item"],
                order__customer=request.user,
            )
            .select_related("order", "product")
            .first()
        )

        if not order_item:
            return Response(
                {"error": {"code": "not_found", "message": "Order item not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order_item.order.status != "delivered":
            return Response(
                {
                    "error": {
                        "code": "review_not_eligible",
                        "message": "Order must be delivered to review.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if hasattr(order_item, "review"):
            return Response(
                {
                    "error": {
                        "code": "duplicate_resource",
                        "message": "Review already exists for this order item.",
                    }
                },
                status=status.HTTP_409_CONFLICT,
            )

        review = Review.objects.create(
            product=order_item.product,
            customer=request.user,
            order_item=order_item,
            rating=serializer.validated_data["rating"],
            title=serializer.validated_data["title"],
            content=serializer.validated_data.get("content", ""),
        )

        for image_url in serializer.validated_data.get("images", []):
            ReviewImage.objects.create(review=review, image=image_url)

        return Response(
            {"data": ReviewSerializer(review).data, "message": "Review created."},
            status=status.HTTP_201_CREATED,
        )


class CustomerReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ReviewSerializer, responses=ReviewSerializer)
    def patch(self, request: Request, review_id: str) -> Response:
        review = get_review_by_id(review_id=review_id)
        if not review or review.customer_id != request.user.id:
            return Response(
                {"error": {"code": "not_found", "message": "Review not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        allowed_fields = ["rating", "title", "content"]
        for field in allowed_fields:
            if field in serializer.validated_data:
                setattr(review, field, serializer.validated_data[field])
        review.save(update_fields=[f for f in allowed_fields if f in serializer.validated_data])

        return Response({"data": ReviewSerializer(review).data, "message": "Review updated."})
