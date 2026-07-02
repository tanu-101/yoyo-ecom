from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.selectors.summary import (
    get_return_rate,
    get_sales_data,
    get_summary,
    get_top_products,
)

from .serializers import SalesQuerySerializer, TopProductsQuerySerializer


class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request: Request) -> Response:
        data = get_summary()
        return Response({"data": data, "message": "Success"})


class SalesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request: Request) -> Response:
        serializer = SalesQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = get_sales_data(
            date_from=serializer.validated_data.get("date_from"),
            date_to=serializer.validated_data.get("date_to"),
            group_by=serializer.validated_data.get("group_by", "day"),
        )
        return Response({"data": data, "message": "Success"})


class TopProductsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request: Request) -> Response:
        serializer = TopProductsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = get_top_products(
            limit=serializer.validated_data.get("limit", 10),
            date_from=serializer.validated_data.get("date_from"),
            date_to=serializer.validated_data.get("date_to"),
        )
        return Response({"data": data, "message": "Success"})


class ReturnsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request: Request) -> Response:
        data = get_return_rate(
            date_from=request.query_params.get("date_from"),
            date_to=request.query_params.get("date_to"),
        )
        return Response({"data": data, "message": "Success"})
