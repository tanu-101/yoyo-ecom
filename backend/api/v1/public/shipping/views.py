from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shipping.selectors.shipping import get_active_shipping_methods

from .serializers import ShippingMethodSerializer


class ShippingMethodListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=ShippingMethodSerializer(many=True))
    def get(self, request: Request) -> Response:
        methods = get_active_shipping_methods()
        return Response(
            {"data": ShippingMethodSerializer(methods, many=True).data, "message": "Success"}
        )
