from __future__ import annotations

from django.urls import path

from . import views

app_name = "customer_notifications"

urlpatterns = [
    path(
        "preferences/", views.NotificationPreferenceView.as_view(), name="notification-preferences"
    ),
    path("", views.NotificationListView.as_view(), name="notification-list"),
]
