from __future__ import annotations

from django.urls import path

from . import views

app_name = "stripe_webhooks"

urlpatterns = [
    path("", views.stripe_webhook, name="stripe-webhook"),
]
