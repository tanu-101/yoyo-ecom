from __future__ import annotations

from django.urls import path

from . import views

app_name = "admin_notifications"

urlpatterns = [
    path("", views.AdminNotificationListView.as_view(), name="notification-list"),
    path(
        "preferences/",
        views.AdminNotificationPreferencesListView.as_view(),
        name="notification-preferences",
    ),
]
