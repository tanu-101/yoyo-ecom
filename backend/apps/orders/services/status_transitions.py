from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.common.exceptions import BusinessRuleViolation
from apps.orders.constants import OrderStatus
from apps.orders.models import Order, OrderStatusHistory

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    OrderStatus.PENDING_PAYMENT: {OrderStatus.PLACED},
    OrderStatus.PLACED: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


@transaction.atomic
def transition_order_status(
    *,
    order: Order,
    to_status: str,
    changed_by: User,
    reason: str = "",
) -> Order:
    if order.status not in ALLOWED_TRANSITIONS:
        raise BusinessRuleViolation(
            f"No transitions allowed from '{order.status}'.",
            code="invalid_order_status_transition",
        )

    if to_status not in ALLOWED_TRANSITIONS[order.status]:
        raise BusinessRuleViolation(
            f"Transition from '{order.status}' to '{to_status}' is not allowed.",
            code="invalid_order_status_transition",
        )

    previous_status = order.status
    order.status = to_status

    timestamp_field = {
        OrderStatus.PLACED: "placed_at",
        OrderStatus.PROCESSING: None,
        OrderStatus.SHIPPED: "shipped_at",
        OrderStatus.DELIVERED: "delivered_at",
    }.get(
        to_status
    )  # type: ignore[call-overload]

    if timestamp_field:
        setattr(order, timestamp_field, timezone.now())

    update_fields = ["status", "updated_at"]
    if timestamp_field:
        update_fields.append(timestamp_field)

    order.save(update_fields=update_fields)

    OrderStatusHistory.objects.create(
        order=order,
        from_status=previous_status,
        to_status=to_status,
        changed_by=changed_by,
        reason=reason,
    )

    if to_status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
        from apps.notifications.services.dispatch import dispatch_order_notifications

        status_display = dict(OrderStatus.choices).get(to_status, to_status)
        dispatch_order_notifications(
            user=order.customer,
            notification_type=f"order_{to_status}",
            subject=f"Order {order.order_number} {status_display}",
            body=f"Your order {order.order_number} has been updated to '{status_display}'.",
        )

    return order
