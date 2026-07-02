from __future__ import annotations

from django.urls import path

from . import views

app_name = "admin_shipping"

urlpatterns = [
    path(
        "orders/<uuid:order_id>/tracking/",
        views.AdminCreateTrackingView.as_view(),
        name="create-tracking",
    ),
    path(
        "orders/<uuid:order_id>/tracking/update/",
        views.AdminUpdateTrackingView.as_view(),
        name="update-tracking",
    ),
]
