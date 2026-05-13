from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
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

    @extend_schema(
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Staff list response",
                value={
                    "data": [
                        {
                            "id": "11111111-1111-1111-1111-111111111111",
                            "email": "staff@example.com",
                            "first_name": "Sam",
                            "last_name": "Staff",
                            "role": "staff",
                            "phone": "+15550000002",
                            "profile_picture": "",
                            "is_active": True,
                            "is_email_verified": False,
                            "is_superuser": False,
                            "permissions": ["manage_orders"],
                        }
                    ],
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request) -> Response:
        users = staff_users(include_inactive=True)
        return Response({"data": [_admin_user_data(user) for user in users], "message": "Success"})

    @extend_schema(
        request=StaffCreateSerializer,
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Staff create request",
                value={
                    "email": "staff@example.com",
                    "password": "StrongPass123",
                    "first_name": "Sam",
                    "last_name": "Staff",
                    "phone": "+15550000002",
                    "profile_picture": "",
                    "permissions": ["manage_orders"],
                },
                request_only=True,
            ),
            OpenApiExample(
                "Staff create response",
                value={
                    "data": {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "email": "staff@example.com",
                        "first_name": "Sam",
                        "last_name": "Staff",
                        "role": "staff",
                        "phone": "+15550000002",
                        "profile_picture": "",
                        "is_active": True,
                        "is_email_verified": False,
                        "is_superuser": False,
                        "permissions": ["manage_orders"],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
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

    @extend_schema(
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Staff detail response",
                value={
                    "data": {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "email": "staff@example.com",
                        "first_name": "Sam",
                        "last_name": "Staff",
                        "role": "staff",
                        "phone": "+15550000002",
                        "profile_picture": "",
                        "is_active": True,
                        "is_email_verified": False,
                        "is_superuser": False,
                        "permissions": ["manage_orders"],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request, user_id) -> Response:
        user = get_user_by_id(user_id)
        if user is None or user.role != "staff":
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"data": _admin_user_data(user), "message": "Success"})

    @extend_schema(
        request=StaffUpdateSerializer,
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Staff update request",
                value={"last_name": "Team", "is_active": True},
                request_only=True,
            ),
            OpenApiExample(
                "Staff update response",
                value={
                    "data": {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "email": "staff@example.com",
                        "first_name": "Sam",
                        "last_name": "Team",
                        "role": "staff",
                        "phone": "+15550000002",
                        "profile_picture": "",
                        "is_active": True,
                        "is_email_verified": False,
                        "is_superuser": False,
                        "permissions": ["manage_orders"],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
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

    @extend_schema(
        request=StaffPermissionUpdateSerializer,
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Staff permissions request",
                value={"permissions": [{"code": "manage_orders", "enabled": True}]},
                request_only=True,
            ),
            OpenApiExample(
                "Staff permissions response",
                value={
                    "data": {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "email": "staff@example.com",
                        "first_name": "Sam",
                        "last_name": "Staff",
                        "role": "staff",
                        "phone": "+15550000002",
                        "profile_picture": "",
                        "is_active": True,
                        "is_email_verified": False,
                        "is_superuser": False,
                        "permissions": ["manage_orders"],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
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
