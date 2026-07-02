from __future__ import annotations

from django.urls import path

from . import views

app_name = "admin_orders"

urlpatterns = [
    path("", views.AdminOrderListView.as_view(), name="order-list"),
    path("<uuid:order_id>/", views.AdminOrderDetailView.as_view(), name="order-detail"),
    path(
        "<uuid:order_id>/status/",
        views.AdminUpdateOrderStatusView.as_view(),
        name="order-update-status",
    ),
    path("<uuid:order_id>/cancel/", views.AdminCancelOrderView.as_view(), name="order-cancel"),
]
