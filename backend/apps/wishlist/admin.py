from __future__ import annotations

from django.contrib import admin

from apps.wishlist.models import WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("customer", "product", "variant", "created_at")
    search_fields = ("customer__email", "product__name")
