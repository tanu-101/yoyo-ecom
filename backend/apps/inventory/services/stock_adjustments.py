from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction

from apps.catalog.models import Variant
from apps.common.exceptions import BusinessRuleViolation
from apps.inventory.models.inventory_transaction import InventoryTransaction

if TYPE_CHECKING:
    from apps.accounts.models import User


@transaction.atomic
def adjust_stock(
    *,
    variant: Variant,
    quantity_changed: int,
    transaction_type: str,
    reference_type: str = "",
    reference_id: str | None = None,
    notes: str = "",
    created_by: User | None = None,
) -> InventoryTransaction:
    """
    Adjusts stock for a variant inside a database transaction with a write lock.
    Creates an InventoryTransaction history record.
    """
    # Write-lock the Variant record to prevent race conditions during updates
    locked_variant = Variant.objects.select_for_update().get(id=variant.id)

    stock_before = locked_variant.stock_quantity
    stock_after = stock_before + quantity_changed

    if stock_after < 0:
        raise BusinessRuleViolation(
            f"Insufficient stock for variant '{locked_variant.sku}'. "
            f"Available: {stock_before}, requested change: {quantity_changed}.",
            code="insufficient_stock",
        )

    locked_variant.stock_quantity = stock_after
    locked_variant.save(update_fields=["stock_quantity"])

    inventory_transaction = InventoryTransaction.objects.create(
        variant=locked_variant,
        transaction_type=transaction_type,
        quantity_changed=quantity_changed,
        stock_before=stock_before,
        stock_after=stock_after,
        reference_type=reference_type,
        reference_id=reference_id,
        notes=notes,
        created_by=created_by,
    )

    # Sync back the updated variant quantity to the original instance reference
    variant.stock_quantity = stock_after

    return inventory_transaction
