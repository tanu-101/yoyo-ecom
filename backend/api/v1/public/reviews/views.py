from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reviews.selectors.reviews import get_approved_reviews_for_product

from .serializers import PublicReviewSerializer


class PublicProductReviewListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=PublicReviewSerializer(many=True))
    def get(self, request: Request, product_id: str) -> Response:
        reviews = get_approved_reviews_for_product(product_id=product_id)
        return Response(
            {"data": PublicReviewSerializer(reviews, many=True).data, "message": "Success"}
        )
