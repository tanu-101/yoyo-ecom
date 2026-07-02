from __future__ import annotations

from django.contrib import admin

from apps.orders.models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product_name",
        "variant_name",
        "sku",
        "quantity",
        "unit_price",
        "line_total",
    )


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("from_status", "to_status", "changed_by", "reason", "created_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer",
        "status",
        "payment_status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "payment_status", "created_at")
    search_fields = (
        "order_number",
        "customer__email",
        "customer__first_name",
        "customer__last_name",
    )
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [OrderItemInline, OrderStatusHistoryInline]
