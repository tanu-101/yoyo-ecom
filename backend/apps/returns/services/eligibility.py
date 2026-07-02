from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import User
from apps.common.exceptions import BusinessRuleViolation
from apps.orders.constants import OrderStatus
from apps.orders.selectors.orders import get_order_items
from apps.returns.models import ReturnRequest

RETURN_WINDOW_DAYS = 30


def validate_return_eligibility(*, customer: User, order) -> None:
    if order.customer_id != customer.id:
        raise BusinessRuleViolation(
            "Order does not belong to this customer.", code="permission_denied"
        )

    if order.status != OrderStatus.DELIVERED:
        raise BusinessRuleViolation(
            "Order must be delivered before requesting a return.", code="return_not_eligible"
        )

    if order.delivered_at:
        if timezone.now() - order.delivered_at > timedelta(days=RETURN_WINDOW_DAYS):
            raise BusinessRuleViolation(
                "Return window has expired. Must be requested within 30 days of delivery.",
                code="return_window_expired",
            )


def validate_return_quantity(*, order, items_data: list[dict]) -> None:
    order_items = get_order_items(order=order)
    order_item_map = {str(item.id): item for item in order_items}

    for item_data in items_data:
        order_item_id = str(item_data["order_item"])
        quantity = item_data["quantity"]

        order_item = order_item_map.get(order_item_id)
        if not order_item:
            raise BusinessRuleViolation(
                f"Order item {order_item_id} not found in this order.",
                code="invalid_order_item",
            )

        if quantity <= 0:
            raise BusinessRuleViolation(
                "Quantity must be greater than zero.", code="invalid_quantity"
            )

        if quantity > order_item.quantity:
            raise BusinessRuleViolation(
                f"Return quantity ({quantity}) exceeds purchased quantity ({order_item.quantity}).",
                code="invalid_quantity",
            )

        already_returned = (
            ReturnRequest.objects.filter(
                items__order_item=order_item,
                status__in=[
                    "pending_review",
                    "approved",
                    "awaiting_return",
                    "in_transit",
                    "received",
                ],
            )
            .distinct()
            .count()
        )

        if already_returned > 0:
            raise BusinessRuleViolation(
                f"Order item {order_item_id} already has a pending return request.",
                code="duplicate_return",
            )
