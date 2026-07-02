from __future__ import annotations

from django.urls import path

from . import views

app_name = "admin_analytics"

urlpatterns = [
    path("summary/", views.SummaryView.as_view(), name="analytics-summary"),
    path("sales/", views.SalesView.as_view(), name="analytics-sales"),
    path("products/top/", views.TopProductsView.as_view(), name="analytics-top-products"),
    path("returns/", views.ReturnsView.as_view(), name="analytics-returns"),
]
