from __future__ import annotations

from django.urls import include, path

app_name = "admin_api"

urlpatterns = [
    path("users/", include("api.v1.admin.users.urls")),
    path("staff/", include("api.v1.admin.staff.urls")),
    path("catalog/", include("api.v1.admin.catalog.urls")),
    path("inventory/", include("api.v1.admin.inventory.urls")),
    path("orders/", include("api.v1.admin.orders.urls")),
    path("payments/", include("api.v1.admin.payments.urls")),
    path("shipping/", include("api.v1.admin.shipping.urls")),
    path("returns/", include("api.v1.admin.returns.urls")),
    path("reviews/", include("api.v1.admin.reviews.urls")),
    path("coupons/", include("api.v1.admin.coupons.urls")),
    path("notifications/", include("api.v1.admin.notifications.urls")),
    path("analytics/", include("api.v1.admin.analytics.urls")),
]
