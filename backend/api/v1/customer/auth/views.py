from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.selectors.users import user_permissions
from apps.accounts.services import authentication
from apps.common.exceptions import DomainError

from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    RefreshSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserSummarySerializer,
    VerifyEmailSerializer,
)


def _error(exc: Exception, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    code = getattr(exc, "code", "validation_error")
    message = getattr(exc, "message", str(exc))
    if isinstance(exc, DjangoValidationError):
        message = "; ".join(exc.messages)
    return Response({"error": {"code": code, "message": message, "fields": {}}}, status=status_code)


def _user_data(user) -> dict:
    return UserSummarySerializer(
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "phone": user.phone,
            "profile_picture": user.profile_picture,
            "is_email_verified": user.is_email_verified,
            "permissions": user_permissions(user),
        }
    ).data


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                "Register request",
                value={
                    "email": "customer@example.com",
                    "password": "StrongPass123",
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "phone": "+15550000000",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Register response",
                value={
                    "data": {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "email": "customer@example.com",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "role": "customer",
                        "phone": "+15550000000",
                        "profile_picture": "",
                        "is_email_verified": False,
                        "permissions": [],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = authentication.register_customer(**serializer.validated_data)
        except (DomainError, DjangoValidationError) as exc:
            return _error(exc)
        return Response(
            {"data": _user_data(user), "message": "Success"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Login request",
                value={"email": "customer@example.com", "password": "StrongPass123"},
                request_only=True,
            ),
            OpenApiExample(
                "Login response",
                value={
                    "data": {
                        "access": "eyJhbGciOiJIUzI1NiIs...",
                        "refresh": "eyJhbGciOiJIUzI1NiIs...",
                        "user": {
                            "id": "11111111-1111-1111-1111-111111111111",
                            "email": "customer@example.com",
                            "first_name": "Jane",
                            "last_name": "Doe",
                            "role": "customer",
                            "phone": "+15550000000",
                            "profile_picture": "",
                            "is_email_verified": False,
                            "permissions": [],
                        },
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = authentication.authenticate_user(**serializer.validated_data)
        except DomainError as exc:
            return _error(exc, status.HTTP_401_UNAUTHORIZED)
        return Response(
            {
                "data": {
                    **authentication.issue_tokens(user),
                    "user": _user_data(user),
                },
                "message": "Success",
            }
        )


class RefreshView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RefreshSerializer,
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Refresh request",
                value={"refresh": "eyJhbGciOiJIUzI1NiIs..."},
                request_only=True,
            ),
            OpenApiExample(
                "Refresh response",
                value={"data": {"access": "eyJhbGciOiJIUzI1NiIs..."}, "message": "Success"},
                response_only=True,
            ),
        ],
    )
    def post(self, request) -> Response:
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
        except Exception as exc:
            return _error(exc, status.HTTP_401_UNAUTHORIZED)
        return Response({"data": {"access": str(refresh.access_token)}, "message": "Success"})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={204: None},
        examples=[
            OpenApiExample(
                "Logout request",
                value={"refresh": "eyJhbGciOiJIUzI1NiIs..."},
                request_only=True,
            ),
        ],
    )
    def post(self, request) -> Response:
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            authentication.logout_refresh_token(serializer.validated_data["refresh"])
        except DomainError as exc:
            return _error(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Me response",
                value={
                    "data": {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "email": "customer@example.com",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "role": "customer",
                        "phone": "+15550000000",
                        "profile_picture": "",
                        "is_email_verified": True,
                        "permissions": [],
                    },
                    "message": "Success",
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request) -> Response:
        return Response({"data": _user_data(request.user), "message": "Success"})


class RequestEmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Request email verification response",
                value={"data": {}, "message": "Verification code sent."},
                response_only=True,
            ),
        ],
    )
    def post(self, request) -> Response:
        authentication.request_email_verification(request.user)
        return Response({"data": {}, "message": "Verification code sent."})


class VerifyEmailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=VerifyEmailSerializer,
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Verify email request",
                value={"code": "123456"},
                request_only=True,
            ),
            OpenApiExample(
                "Verify email response",
                value={
                    "data": {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "email": "customer@example.com",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "role": "customer",
                        "phone": "+15550000000",
                        "profile_picture": "",
                        "is_email_verified": True,
                        "permissions": [],
                    },
                    "message": "Email verified.",
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request) -> Response:
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            authentication.verify_email(user=request.user, **serializer.validated_data)
        except DomainError as exc:
            return _error(exc)
        return Response({"data": _user_data(request.user), "message": "Email verified."})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Forgot password request",
                value={"email": "customer@example.com"},
                request_only=True,
            ),
            OpenApiExample(
                "Forgot password response",
                value={"data": {}, "message": "If the email exists, a reset code was sent."},
                response_only=True,
            ),
        ],
    )
    def post(self, request) -> Response:
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        authentication.request_password_reset(serializer.validated_data["email"])
        return Response({"data": {}, "message": "If the email exists, a reset code was sent."})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ResetPasswordSerializer,
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Reset password request",
                value={
                    "email": "customer@example.com",
                    "code": "123456",
                    "new_password": "NewStrongPass123",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Reset password response",
                value={"data": {}, "message": "Password reset successful."},
                response_only=True,
            ),
        ],
    )
    def post(self, request) -> Response:
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            authentication.reset_password(**serializer.validated_data)
        except (DomainError, DjangoValidationError) as exc:
            return _error(exc)
        return Response({"data": {}, "message": "Password reset successful."})
