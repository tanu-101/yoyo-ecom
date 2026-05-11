from __future__ import annotations

from django.urls import include, path

from api.health import health_check

app_name = "public"

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("catalog/", include("api.v1.public.catalog.urls")),
    path("reviews/", include("api.v1.public.reviews.urls")),
    path("shipping/", include("api.v1.public.shipping.urls")),
]
