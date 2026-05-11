from __future__ import annotations

from django.urls import include, path

app_name = "webhooks"

urlpatterns = [
    path("stripe/", include("api.v1.webhooks.stripe.urls")),
]

