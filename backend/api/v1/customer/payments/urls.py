from __future__ import annotations

from django.urls import path

from . import views

app_name = "customer_payments"

urlpatterns = [
    path("create-intent/", views.CreatePaymentIntentView.as_view(), name="create-intent"),
    path("", views.CustomerPaymentListView.as_view(), name="payment-list"),
    path("<uuid:payment_id>/", views.CustomerPaymentDetailView.as_view(), name="payment-detail"),
]
