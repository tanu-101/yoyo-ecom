from __future__ import annotations

from django.urls import path

from . import views

app_name = "public_reviews"

urlpatterns = [
    path(
        "products/<uuid:product_id>/",
        views.PublicProductReviewListView.as_view(),
        name="product-reviews",
    ),
]
