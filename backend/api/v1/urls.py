from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("auth/", include("api.v1.accounts.urls")),
    path("users/", include("api.v1.accounts.user_urls")),
    path("catalog/", include("api.v1.catalog.urls")),
    path("inventory/", include("api.v1.inventory.urls")),
    path("cart/", include("api.v1.carts.urls")),
    path("orders/", include("api.v1.orders.urls")),
    path("payments/", include("api.v1.payments.urls")),
    path("shipping/", include("api.v1.shipping.urls")),
    path("returns/", include("api.v1.returns.urls")),
    path("reviews/", include("api.v1.reviews.urls")),
    path("wishlist/", include("api.v1.wishlist.urls")),
    path("coupons/", include("api.v1.coupons.urls")),
    path("notifications/", include("api.v1.notifications.urls")),
    path("analytics/", include("api.v1.analytics.urls")),
]

