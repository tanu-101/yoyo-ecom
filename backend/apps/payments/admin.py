from __future__ import annotations

from django.contrib import admin

from apps.payments.models import Payment, PaymentEvent, Refund


class RefundInline(admin.TabularInline):
    model = Refund
    extra = 0
    readonly_fields = ("amount", "reason", "status", "created_at", "processed_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "provider", "amount", "status", "created_at")
    list_filter = ("status", "provider", "created_at")
    search_fields = ("order__order_number", "provider_payment_intent_id")
    readonly_fields = ("created_at", "updated_at", "processed_at")
    inlines = [RefundInline]


@admin.register(PaymentEvent)
class PaymentEventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "event_type", "processed_at", "created_at")
    list_filter = ("event_type", "processed_at")
    search_fields = ("event_id",)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("id", "payment", "amount", "status", "created_at")
    list_filter = ("status",)
