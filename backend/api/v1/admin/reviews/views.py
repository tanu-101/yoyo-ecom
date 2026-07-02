from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import BusinessRuleViolation
from apps.reviews.selectors.reviews import get_review_by_id, get_reviews_for_admin
from apps.reviews.services.moderation import approve_review, reject_review


class AdminReviewListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request: Request) -> Response:
        reviews = get_reviews_for_admin()
        from api.v1.customer.reviews.serializers import ReviewSerializer

        return Response({"data": ReviewSerializer(reviews, many=True).data, "message": "Success"})


class AdminApproveReviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=dict)
    def post(self, request: Request, review_id: str) -> Response:
        review = get_review_by_id(review_id=review_id)
        if not review:
            return Response(
                {"error": {"code": "not_found", "message": "Review not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            review = approve_review(review=review)
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from api.v1.customer.reviews.serializers import ReviewSerializer

        return Response({"data": ReviewSerializer(review).data, "message": "Review approved."})


class AdminRejectReviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=dict)
    def post(self, request: Request, review_id: str) -> Response:
        review = get_review_by_id(review_id=review_id)
        if not review:
            return Response(
                {"error": {"code": "not_found", "message": "Review not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            review = reject_review(review=review)
        except BusinessRuleViolation as exc:
            return Response(
                {"error": {"code": exc.code, "message": exc.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from api.v1.customer.reviews.serializers import ReviewSerializer

        return Response({"data": ReviewSerializer(review).data, "message": "Review rejected."})
