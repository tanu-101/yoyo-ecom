from __future__ import annotations

from django.urls import path

from . import views

app_name = "admin_payments"

urlpatterns = [
    path("", views.AdminPaymentListView.as_view(), name="payment-list"),
    path("<uuid:payment_id>/", views.AdminPaymentDetailView.as_view(), name="payment-detail"),
    path("<uuid:payment_id>/refund/", views.AdminRefundView.as_view(), name="payment-refund"),
]
