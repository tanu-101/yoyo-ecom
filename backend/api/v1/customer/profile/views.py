from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.customer.auth.views import _error, _user_data
from apps.accounts.services.authentication import change_password
from apps.accounts.services.users import update_user_profile, update_user_profile_image
from apps.common.exceptions import DomainError

from .serializers import ChangePasswordSerializer, ProfileImageSerializer, ProfileUpdateSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        return Response({"data": _user_data(request.user), "message": "Success"})

    def patch(self, request) -> Response:
        serializer = ProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = update_user_profile(request.user, serializer.validated_data)
        return Response({"data": _user_data(user), "message": "Success"})


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request) -> Response:
        serializer = ProfileImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = update_user_profile_image(
            user=request.user,
            profile_picture=serializer.validated_data["profile_picture"],
        )
        return Response({"data": _user_data(user), "message": "Success"})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            change_password(user=request.user, **serializer.validated_data)
        except (DomainError, DjangoValidationError) as exc:
            return _error(exc)
        return Response({"data": {}, "message": "Password changed."})
