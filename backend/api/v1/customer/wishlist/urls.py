from __future__ import annotations

from django.urls import path

from . import views

app_name = "customer_wishlist"

urlpatterns = [
    path("", views.WishlistListView.as_view(), name="wishlist-list"),
    path("<uuid:item_id>/", views.WishlistDetailView.as_view(), name="wishlist-detail"),
    path(
        "<uuid:item_id>/move-to-cart/", views.MoveToCartView.as_view(), name="wishlist-move-to-cart"
    ),
]
