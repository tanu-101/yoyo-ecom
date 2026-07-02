from __future__ import annotations

from django.contrib import admin

from apps.catalog.models import (
    Category,
    Product,
    ProductImage,
    Variant,
    VariantAttribute,
    VariantAttributeValue,
    VariantOption,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("created_at",)


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "category", "status", "base_price", "is_featured", "created_at")
    list_filter = ("status", "is_featured", "category")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductImageInline, VariantInline]


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "product", "price", "stock_quantity", "status")
    list_filter = ("status", "product__category")
    search_fields = ("sku", "name", "product__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("image", "product", "is_primary", "sort_order")
    list_filter = ("is_primary",)
    search_fields = ("product__name",)


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value", "slug")
    prepopulated_fields = {"slug": ("value",)}
    list_filter = ("attribute",)
    search_fields = ("value",)


@admin.register(VariantOption)
class VariantOptionAdmin(admin.ModelAdmin):
    list_display = ("variant", "attribute", "value")
    list_filter = ("attribute",)
    search_fields = ("variant__sku", "variant__product__name")
