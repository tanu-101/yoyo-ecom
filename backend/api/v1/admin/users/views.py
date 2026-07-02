from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.customer.auth.views import _error
from apps.accounts.selectors.users import get_user_by_id, user_permissions, users_list
from apps.accounts.services.users import (
    activate_user,
    admin_update_user,
    create_user,
    deactivate_user,
    reset_user_password,
    set_user_role,
    soft_delete_user,
)
from apps.common.exceptions import DomainError
from apps.common.permissions import IsAdmin

from .serializers import (
    AdminUserCreateSerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
    PasswordResetSerializer,
    SetRoleSerializer,
)


def _admin_user_data(user) -> dict:
    return AdminUserSerializer(
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "phone": user.phone,
            "profile_picture": user.profile_picture,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "is_superuser": user.is_superuser,
            "permissions": user_permissions(user),
        }
    ).data


def _get_target(user_id):
    return get_user_by_id(user_id, include_deleted=False)


class AdminUserListCreateView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        operation_id="v1_admin_users_list",
        responses=dict,
        examples=[
            OpenApiExample(
                "Admin user list response",
                value={
                    "data": [
                        {
                            "id": "11111111-1111-1111-1111-111111111111",
                            "email": "admin@example.com",
                            "first_name": "Admin",
                            "last_name": "User",
                            "role": "admin",
                            "phone": "+15550000001",
                            "profile_picture": "",
                            "is_active": True,
                            "is_email_verified": True,
                            "is_superuser": False,
                            "permissions": ["manage_users"],
                        }
                    ],
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request) -> Response:
        is_active = request.query_params.get("is_active")
        active_filter = None
        if is_active is not None:
            active_filter = is_active.lower() in {"1", "true", "yes"}
        users = users_list(
            role=request.query_params.get("role") or None,
            is_active=active_filter,
            search=request.query_params.get("search") or None,
        )
        return Response({"data": [_admin_user_data(user) for user in users], "message": "Success"})

    @extend_schema(
        request=AdminUserCreateSerializer,
        responses=dict,
        examples=[
            OpenApiExample(
                "Admin user create request",
                value={
                    "email": "staff@example.com",
                    "password": "StrongPass123",
                    "role": "staff",
                    "first_name": "Sam",
                    "last_name": "Staff",
                    "phone": "+15550000002",
                    "profile_picture": "",
                    "is_active": True,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Admin user create response",
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
                        "permissions": [],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request) -> Response:
        serializer = AdminUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = create_user(**serializer.validated_data)
        except (DomainError, DjangoValidationError) as exc:
            return _error(exc)
        return Response(
            {"data": _admin_user_data(user), "message": "Success"},
            status=status.HTTP_201_CREATED,
        )


class AdminUserDetailView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        responses=dict,
        examples=[
            OpenApiExample(
                "Admin user detail response",
                value={
                    "data": {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "email": "admin@example.com",
                        "first_name": "Admin",
                        "last_name": "User",
                        "role": "admin",
                        "phone": "+15550000001",
                        "profile_picture": "",
                        "is_active": True,
                        "is_email_verified": True,
                        "is_superuser": False,
                        "permissions": ["manage_users"],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request, user_id) -> Response:
        user = _get_target(user_id)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"data": _admin_user_data(user), "message": "Success"})

    @extend_schema(
        request=AdminUserUpdateSerializer,
        responses=dict,
        examples=[
            OpenApiExample(
                "Admin user update request",
                value={"last_name": "Manager", "is_active": True},
                request_only=True,
            ),
            OpenApiExample(
                "Admin user update response",
                value={
                    "data": {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "email": "admin@example.com",
                        "first_name": "Admin",
                        "last_name": "Manager",
                        "role": "admin",
                        "phone": "+15550000001",
                        "profile_picture": "",
                        "is_active": True,
                        "is_email_verified": True,
                        "is_superuser": False,
                        "permissions": ["manage_users"],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def patch(self, request, user_id) -> Response:
        user = _get_target(user_id)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AdminUserUpdateSerializer(data=request.data, partial=True)
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


class AdminUserActionView(APIView):
    permission_classes = [IsAdmin]
    action = ""

    @extend_schema(
        request=None,
        responses=dict,
        examples=[
            OpenApiExample(
                "Admin user action response",
                value={
                    "data": {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "email": "admin@example.com",
                        "first_name": "Admin",
                        "last_name": "User",
                        "role": "admin",
                        "phone": "+15550000001",
                        "profile_picture": "",
                        "is_active": True,
                        "is_email_verified": True,
                        "is_superuser": False,
                        "permissions": ["manage_users"],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request, user_id) -> Response:
        user = _get_target(user_id)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            if self.action == "activate":
                user = activate_user(actor=request.user, target_user=user)
            elif self.action == "deactivate":
                user = deactivate_user(actor=request.user, target_user=user)
            elif self.action == "soft_delete":
                user = soft_delete_user(actor=request.user, target_user=user)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except DomainError as exc:
            return _error(exc)
        return Response({"data": _admin_user_data(user), "message": "Success"})


class AdminResetPasswordView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        request=PasswordResetSerializer,
        responses=dict,
        examples=[
            OpenApiExample(
                "Admin reset password request",
                value={"new_password": "NewStrongPass123"},
                request_only=True,
            ),
            OpenApiExample(
                "Admin reset password response",
                value={"data": {}, "message": "Password reset successful."},
                response_only=True,
            ),
        ],
    )
    def post(self, request, user_id) -> Response:
        user = _get_target(user_id)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reset_user_password(
                actor=request.user,
                target_user=user,
                new_password=serializer.validated_data["new_password"],
            )
        except (DomainError, DjangoValidationError) as exc:
            return _error(exc)
        return Response({"data": {}, "message": "Password reset successful."})


class AdminSetRoleView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        request=SetRoleSerializer,
        responses=dict,
        examples=[
            OpenApiExample(
                "Admin set role request",
                value={"role": "staff"},
                request_only=True,
            ),
            OpenApiExample(
                "Admin set role response",
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
                        "permissions": [],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request, user_id) -> Response:
        user = _get_target(user_id)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SetRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = set_user_role(
                actor=request.user,
                target_user=user,
                role=serializer.validated_data["role"],
            )
        except DomainError as exc:
            return _error(exc)
        return Response({"data": _admin_user_data(user), "message": "Success"})
