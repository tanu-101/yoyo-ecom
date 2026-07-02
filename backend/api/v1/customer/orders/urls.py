from __future__ import annotations

from django.urls import path

from . import views

app_name = "customer_orders"

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("", views.CustomerOrderListView.as_view(), name="order-list"),
    path("<uuid:order_id>/", views.CustomerOrderDetailView.as_view(), name="order-detail"),
    path("<uuid:order_id>/cancel/", views.CustomerCancelOrderView.as_view(), name="order-cancel"),
]
