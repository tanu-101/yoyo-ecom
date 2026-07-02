from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.common.exceptions import BusinessRuleViolation
from apps.inventory.constants import InventoryTransactionType
from apps.inventory.services.stock_adjustments import adjust_stock
from apps.orders.constants import OrderStatus
from apps.orders.models import Order, OrderStatusHistory
from apps.orders.selectors.orders import get_order_items

VALID_CUSTOMER_CANCEL_STATUSES = {OrderStatus.PENDING_PAYMENT, OrderStatus.PLACED}
VALID_ADMIN_CANCEL_STATUSES = {
    OrderStatus.PENDING_PAYMENT,
    OrderStatus.PLACED,
    OrderStatus.PROCESSING,
}


@transaction.atomic
def cancel_order(
    *,
    order: Order,
    cancelled_by: User,
    reason: str = "",
) -> Order:
    if cancelled_by == order.customer or cancelled_by.is_superuser:
        if cancelled_by.is_superuser or cancelled_by.role == "admin":
            valid_statuses = VALID_ADMIN_CANCEL_STATUSES
        else:
            valid_statuses = VALID_CUSTOMER_CANCEL_STATUSES
    else:
        from apps.accounts.constants import UserRole

        if cancelled_by.role in (UserRole.ADMIN, UserRole.STAFF):
            valid_statuses = VALID_ADMIN_CANCEL_STATUSES
        else:
            valid_statuses = set()

    if order.status not in valid_statuses:
        raise BusinessRuleViolation(
            f"Order cannot be cancelled in '{order.status}' status.",
            code="invalid_order_status_transition",
        )

    previous_status = order.status
    order.status = OrderStatus.CANCELLED
    order.cancelled_at = timezone.now()
    order.cancelled_by = cancelled_by
    order.cancellation_reason = reason
    order.save(
        update_fields=[
            "status",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
            "updated_at",
        ]
    )

    OrderStatusHistory.objects.create(
        order=order,
        from_status=previous_status,
        to_status=OrderStatus.CANCELLED,
        changed_by=cancelled_by,
        reason=reason or "Order cancelled.",
    )

    items = get_order_items(order=order)
    for item in items:
        adjust_stock(
            variant=item.variant,
            quantity_changed=item.quantity,
            transaction_type=InventoryTransactionType.CANCELLATION,
            reference_type="order",
            reference_id=order.id,
            notes=f"Cancellation of order {order.order_number}",
        )

    from apps.notifications.services.dispatch import dispatch_order_notifications

    dispatch_order_notifications(
        user=order.customer,
        notification_type="order_cancelled",
        subject=f"Order {order.order_number} cancelled",
        body=f"Your order {order.order_number} has been cancelled.",
    )

    return order
