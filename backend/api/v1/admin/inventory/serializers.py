from __future__ import annotations

from rest_framework import serializers

from apps.inventory.models.inventory_transaction import InventoryTransaction
from apps.inventory.models.stock_reservation import StockReservation


class InventoryTransactionSerializer(serializers.ModelSerializer[InventoryTransaction]):
    created_by_email = serializers.SerializerMethodField()

    class Meta:
        model = InventoryTransaction
        fields = [
            "id",
            "variant",
            "transaction_type",
            "quantity_changed",
            "stock_before",
            "stock_after",
            "reference_type",
            "reference_id",
            "notes",
            "created_by",
            "created_by_email",
            "created_at",
        ]
        read_only_fields = fields

    def get_created_by_email(self, obj: InventoryTransaction) -> str:
        if obj.created_by:
            return obj.created_by.email
        return ""


class StockReservationSerializer(serializers.ModelSerializer[StockReservation]):
    class Meta:
        model = StockReservation
        fields = [
            "id",
            "variant",
            "user",
            "order",
            "quantity",
            "status",
            "expires_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class StockAdjustmentSerializer(serializers.Serializer):
    variant_id = serializers.UUIDField()
    quantity_changed = serializers.IntegerField(
        help_text="Positive to add stock, negative to reduce stock."
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_quantity_changed(self, value: int) -> int:
        if value == 0:
            raise serializers.ValidationError("quantity_changed must not be zero.")
        return value


class VariantStockSummarySerializer(serializers.Serializer):
    variant_id = serializers.UUIDField()
    sku = serializers.CharField()
    physical_stock = serializers.IntegerField()
    active_reservations = serializers.IntegerField()
    net_available = serializers.IntegerField()
