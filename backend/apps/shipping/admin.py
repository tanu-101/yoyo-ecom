from __future__ import annotations

from django.contrib import admin

from apps.shipping.models import OrderShippingAddress, OrderTracking, ShippingMethod


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "base_price", "is_active")
    list_filter = ("is_active",)


@admin.register(OrderShippingAddress)
class OrderShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("order", "full_name", "city", "country")
    search_fields = ("order__order_number", "full_name")


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ("order", "carrier", "tracking_number", "status")
    list_filter = ("status", "carrier")
