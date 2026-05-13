from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.admin.users.views import _admin_user_data
from api.v1.customer.auth.views import _error
from apps.accounts.selectors.users import get_user_by_id, staff_users
from apps.accounts.services.staff_permissions import set_staff_permissions
from apps.accounts.services.users import admin_update_user, create_staff_user
from apps.common.exceptions import DomainError
from apps.common.permissions import IsAdmin

from .serializers import (
    StaffCreateSerializer,
    StaffPermissionUpdateSerializer,
    StaffUpdateSerializer,
)


class StaffListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request) -> Response:
        users = staff_users(include_inactive=True)
        return Response({"data": [_admin_user_data(user) for user in users], "message": "Success"})

    def post(self, request) -> Response:
        serializer = StaffCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        permissions = data.pop("permissions", [])
        try:
            user = create_staff_user(
                granted_by=request.user,
                permissions=permissions,
                **data,
            )
        except (DomainError, DjangoValidationError) as exc:
            return _error(exc)
        return Response(
            {"data": _admin_user_data(user), "message": "Success"},
            status=status.HTTP_201_CREATED,
        )


class StaffDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, user_id) -> Response:
        user = get_user_by_id(user_id)
        if user is None or user.role != "staff":
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"data": _admin_user_data(user), "message": "Success"})

    def patch(self, request, user_id) -> Response:
        user = get_user_by_id(user_id)
        if user is None or user.role != "staff":
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = StaffUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            user = admin_update_user(
                actor=request.user,
                target_user=user,
                data=serializer.validated_data,
            )
        except DomainError as exc:
            return _error(exc)
        return Response({"data": _admin_user_data(user), "message": "Success"})


class StaffPermissionsView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, user_id) -> Response:
        user = get_user_by_id(user_id)
        if user is None or user.role != "staff":
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = StaffPermissionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            set_staff_permissions(
                staff_user=user,
                permission_updates=serializer.validated_data["permissions"],
                granted_by=request.user,
            )
        except DomainError as exc:
            return _error(exc)
        return Response({"data": _admin_user_data(user), "message": "Success"})
