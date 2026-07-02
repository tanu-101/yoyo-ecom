from __future__ import annotations

from django.urls import path

from . import views

app_name = "admin_returns"

urlpatterns = [
    path("", views.AdminReturnListView.as_view(), name="return-list"),
    path("<uuid:return_id>/", views.AdminReturnDetailView.as_view(), name="return-detail"),
    path(
        "<uuid:return_id>/approve/", views.AdminApproveReturnView.as_view(), name="return-approve"
    ),
    path("<uuid:return_id>/reject/", views.AdminRejectReturnView.as_view(), name="return-reject"),
    path(
        "<uuid:return_id>/mark-received/",
        views.AdminMarkReceivedView.as_view(),
        name="return-mark-received",
    ),
    path(
        "<uuid:return_id>/process/", views.AdminProcessReturnView.as_view(), name="return-process"
    ),
]
