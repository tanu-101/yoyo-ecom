from __future__ import annotations

from django.urls import path

from .views import (
    InventoryTransactionListView,
    StockAdjustmentView,
    StockReservationListView,
    VariantStockSummaryView,
)

urlpatterns = [
    path("adjustments/", StockAdjustmentView.as_view(), name="admin-inventory-adjust"),
    path("reservations/", StockReservationListView.as_view(), name="admin-inventory-reservations"),
    path(
        "variants/<uuid:variant_id>/stock/",
        VariantStockSummaryView.as_view(),
        name="admin-inventory-stock-summary",
    ),
    path(
        "variants/<uuid:variant_id>/transactions/",
        InventoryTransactionListView.as_view(),
        name="admin-inventory-transactions",
    ),
]
