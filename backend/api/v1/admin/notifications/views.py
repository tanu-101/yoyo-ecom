from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.selectors.notifications import get_notifications_for_user

from .serializers import (
    AdminNotificationPreferenceSerializer,
    AdminNotificationSerializer,
)


class AdminNotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=AdminNotificationSerializer(many=True))
    def get(self, request: Request) -> Response:
        user_id = request.query_params.get("user_id")
        if user_id:
            from apps.accounts.selectors.users import get_user_by_id

            user = get_user_by_id(user_id=user_id)
            if not user:
                return Response(
                    {"error": {"code": "not_found", "message": "User not found."}},
                    status=404,
                )
            notifications = get_notifications_for_user(user=user)
        else:
            notifications = (
                Notification.objects.all().select_related("user").order_by("-created_at")
            )

        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        start = (page - 1) * page_size
        end = start + page_size
        total = notifications.count()
        total_pages = (total + page_size - 1) // page_size

        return Response(
            {
                "data": AdminNotificationSerializer(notifications[start:end], many=True).data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                },
            }
        )


class AdminNotificationPreferencesListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=AdminNotificationPreferenceSerializer(many=True))
    def get(self, request: Request) -> Response:
        user_id = request.query_params.get("user_id")
        if user_id:
            from apps.accounts.selectors.users import get_user_by_id

            user = get_user_by_id(user_id=user_id)
            if not user:
                return Response(
                    {"error": {"code": "not_found", "message": "User not found."}},
                    status=404,
                )
            prefs = NotificationPreference.objects.filter(user=user)
        else:
            prefs = NotificationPreference.objects.all().select_related("user")

        return Response(
            {
                "data": AdminNotificationPreferenceSerializer(prefs, many=True).data,
                "message": "Success",
            }
        )
