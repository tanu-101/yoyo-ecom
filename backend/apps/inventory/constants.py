from django.db import models


class InventoryTransactionType(models.TextChoices):
    ORDER_PLACED = "order_placed", "Order placed"
    CANCELLATION = "cancellation", "Cancellation"
    RETURN_RECEIVED = "return_received", "Return received"
    REFUND = "refund", "Refund"
    MANUAL_ADJUSTMENT = "manual_adjustment", "Manual adjustment"
    CORRECTION = "correction", "Correction"


class StockReservationStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CONSUMED = "consumed", "Consumed"
    RELEASED = "released", "Released"
    EXPIRED = "expired", "Expired"
