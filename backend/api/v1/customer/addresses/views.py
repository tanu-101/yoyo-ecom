from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.selectors.addresses import addresses_for_user, get_address_for_user
from apps.accounts.services.addresses import (
    create_address,
    delete_address,
    set_default_address,
    update_address,
)

from .serializers import AddressSerializer, AddressUpdateSerializer


def _address_data(address) -> dict:
    return AddressSerializer(address).data


class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        serializer = AddressSerializer(addresses_for_user(request.user), many=True)
        return Response({"data": serializer.data, "message": "Success"})

    def post(self, request) -> Response:
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = create_address(user=request.user, data=serializer.validated_data)
        return Response(
            {"data": _address_data(address), "message": "Success"},
            status=status.HTTP_201_CREATED,
        )


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_address(self, request, address_id):
        address = get_address_for_user(request.user, address_id)
        if address is None:
            return None
        return address

    def get(self, request, address_id) -> Response:
        address = self._get_address(request, address_id)
        if address is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"data": _address_data(address), "message": "Success"})

    def patch(self, request, address_id) -> Response:
        address = self._get_address(request, address_id)
        if address is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AddressUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        address = update_address(user=request.user, address=address, data=serializer.validated_data)
        return Response({"data": _address_data(address), "message": "Success"})

    def delete(self, request, address_id) -> Response:
        address = self._get_address(request, address_id)
        if address is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        delete_address(user=request.user, address=address)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetDefaultAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, address_id) -> Response:
        address = get_address_for_user(request.user, address_id)
        if address is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        address = set_default_address(user=request.user, address=address)
        return Response({"data": _address_data(address), "message": "Success"})
