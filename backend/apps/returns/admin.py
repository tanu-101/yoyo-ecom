from __future__ import annotations

from django.contrib import admin

from apps.returns.models import ReturnImage, ReturnItem, ReturnRequest, ReturnStatusHistory


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 0


class ReturnImageInline(admin.TabularInline):
    model = ReturnImage
    extra = 0


class ReturnStatusHistoryInline(admin.TabularInline):
    model = ReturnStatusHistory
    extra = 0
    readonly_fields = ("from_status", "to_status", "changed_by", "created_at")


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("return_number", "order", "customer", "status", "reason", "created_at")
    list_filter = ("status", "reason")
    search_fields = ("return_number", "order__order_number", "customer__email")
    inlines = [ReturnItemInline, ReturnImageInline, ReturnStatusHistoryInline]
