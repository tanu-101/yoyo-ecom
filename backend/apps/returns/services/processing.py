from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.common.exceptions import BusinessRuleViolation
from apps.inventory.constants import InventoryTransactionType
from apps.inventory.services.stock_adjustments import adjust_stock
from apps.returns.models import ReturnRequest, ReturnStatus
from apps.returns.models.status_history import ReturnStatusHistory


@transaction.atomic
def mark_received(
    *,
    return_request: ReturnRequest,
) -> ReturnRequest:
    if return_request.status not in (
        ReturnStatus.APPROVED,
        ReturnStatus.AWAITING_RETURN,
        ReturnStatus.IN_TRANSIT,
    ):
        raise BusinessRuleViolation(
            "Return must be approved or in transit to mark as received.",
            code="invalid_return_status",
        )

    previous_status = return_request.status
    return_request.status = ReturnStatus.RECEIVED
    return_request.received_at = timezone.now()
    return_request.save(update_fields=["status", "received_at", "updated_at"])

    ReturnStatusHistory.objects.create(
        return_request=return_request,
        from_status=previous_status,
        to_status=ReturnStatus.RECEIVED,
        reason="Return items received at warehouse.",
    )

    return return_request


@transaction.atomic
def process_return(
    *,
    return_request: ReturnRequest,
    processed_by: User | None = None,
) -> ReturnRequest:
    if return_request.status != ReturnStatus.RECEIVED:
        raise BusinessRuleViolation(
            "Return must be received before processing.",
            code="invalid_return_status",
        )

    previous_status = return_request.status

    items = return_request.items.select_related("order_item", "order_item__variant").all()
    for item in items:
        variant = item.order_item.variant
        adjust_stock(
            variant=variant,
            quantity_changed=item.quantity,
            transaction_type=InventoryTransactionType.RETURN_RECEIVED,
            reference_type="return",
            reference_id=return_request.id,
            notes=f"Return {return_request.return_number} - stock restocked.",
        )

    resolution = return_request.resolution
    if resolution == "refund":
        return_request.status = ReturnStatus.REFUNDED
    elif resolution == "replacement":
        return_request.status = ReturnStatus.REPLACED
    else:
        return_request.status = ReturnStatus.COMPLETED

    return_request.completed_at = timezone.now()
    return_request.save(update_fields=["status", "completed_at", "updated_at"])

    ReturnStatusHistory.objects.create(
        return_request=return_request,
        from_status=previous_status,
        to_status=return_request.status,
        changed_by=processed_by,
        reason=f"Return processed ({resolution}).",
    )

    return return_request
