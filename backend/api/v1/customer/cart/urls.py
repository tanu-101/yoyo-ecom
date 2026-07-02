from __future__ import annotations

from django.urls import path

from .views import CartItemDetailView, CartItemListView, CartView

urlpatterns = [
    path("", CartView.as_view(), name="customer-cart"),
    path("items/", CartItemListView.as_view(), name="customer-cart-item-list"),
    path("items/<uuid:item_id>/", CartItemDetailView.as_view(), name="customer-cart-item-detail"),
]
