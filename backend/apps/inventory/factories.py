from __future__ import annotations

from datetime import timedelta

import factory
from django.utils import timezone

from apps.accounts.factories import CustomerUserFactory
from apps.catalog.factories import VariantFactory
from apps.inventory.constants import InventoryTransactionType, StockReservationStatus
from apps.inventory.models import InventoryTransaction, StockReservation


class InventoryTransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InventoryTransaction

    variant = factory.SubFactory(VariantFactory)
    transaction_type = InventoryTransactionType.MANUAL_ADJUSTMENT
    quantity_changed = 10
    stock_before = 0
    stock_after = 10
    notes = "Test adjustment"


class StockReservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StockReservation

    variant = factory.SubFactory(VariantFactory)
    user = factory.SubFactory(CustomerUserFactory)
    quantity = 1
    status = StockReservationStatus.ACTIVE
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=24))
