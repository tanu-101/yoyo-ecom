from __future__ import annotations

from django.contrib import admin

from apps.carts.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "variant", "quantity", "unit_price", "display_line_total")
    fields = ("product", "variant", "quantity", "unit_price", "display_line_total")

    @admin.display(description="Line Total")
    def display_line_total(self, obj: CartItem) -> float:
        return obj.line_total


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("customer", "item_count", "created_at", "updated_at")
    search_fields = ("customer__email",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [CartItemInline]

    @admin.display(description="Items")
    def item_count(self, obj: Cart) -> int:
        return obj.items.count()


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "variant", "quantity", "unit_price", "line_total")
    list_filter = ("cart__customer",)
    search_fields = ("cart__customer__email", "variant__sku", "product__name")
    readonly_fields = ("created_at", "updated_at")
