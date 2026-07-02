from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.selectors.notifications import (
    get_notifications_for_user,
    get_preferences_for_user,
)
from apps.notifications.services.notifications import update_preferences

from .serializers import NotificationPreferenceSerializer, NotificationSerializer


class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=NotificationPreferenceSerializer)
    def get(self, request: Request) -> Response:
        pref = get_preferences_for_user(user=request.user)
        return Response({"data": NotificationPreferenceSerializer(pref).data, "message": "Success"})

    @extend_schema(
        request=NotificationPreferenceSerializer, responses=NotificationPreferenceSerializer
    )
    def patch(self, request: Request) -> Response:
        serializer = NotificationPreferenceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        pref = update_preferences(user=request.user, data=serializer.validated_data)
        return Response(
            {"data": NotificationPreferenceSerializer(pref).data, "message": "Preferences updated."}
        )


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=NotificationSerializer(many=True))
    def get(self, request: Request) -> Response:
        notifications = get_notifications_for_user(user=request.user)
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        start = (page - 1) * page_size
        end = start + page_size
        total = notifications.count()
        total_pages = (total + page_size - 1) // page_size

        return Response(
            {
                "data": NotificationSerializer(notifications[start:end], many=True).data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                },
            }
        )
