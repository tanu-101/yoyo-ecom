from __future__ import annotations

from django.urls import include, path

app_name = "public"

urlpatterns = [
    path("catalog/", include("api.v1.public.catalog.urls")),
    path("reviews/", include("api.v1.public.reviews.urls")),
    path("shipping/", include("api.v1.public.shipping.urls")),
]

