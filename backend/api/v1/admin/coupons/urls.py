from __future__ import annotations

from django.urls import path

from . import views

app_name = "admin_coupons"

urlpatterns = [
    path("", views.AdminCouponListView.as_view(), name="coupon-list"),
    path("<uuid:coupon_id>/", views.AdminCouponDetailView.as_view(), name="coupon-detail"),
]
