from __future__ import annotations

from django.contrib import admin

from apps.coupons.models import Coupon, CouponRedemption


class CouponRedemptionInline(admin.TabularInline):
    model = CouponRedemption
    extra = 0
    readonly_fields = ("customer", "order", "discount_amount", "created_at")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "usage_count",
        "is_active",
        "valid_from",
        "valid_until",
    )
    list_filter = ("is_active", "discount_type")
    search_fields = ("code",)
    inlines = [CouponRedemptionInline]
