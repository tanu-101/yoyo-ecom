from __future__ import annotations

from django.contrib import admin

from apps.inventory.models import InventoryTransaction, StockReservation


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "variant",
        "transaction_type",
        "quantity_changed",
        "stock_before",
        "stock_after",
        "created_by",
        "created_at",
    )
    list_filter = ("transaction_type", "created_at")
    search_fields = ("variant__sku", "variant__product__name", "notes")
    readonly_fields = ("created_at",)


@admin.register(StockReservation)
class StockReservationAdmin(admin.ModelAdmin):
    list_display = ("variant", "user", "order", "quantity", "status", "expires_at")
    list_filter = ("status", "expires_at")
    search_fields = ("variant__sku", "user__email")
    readonly_fields = ("created_at", "updated_at")
