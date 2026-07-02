from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.orders.models import Order, OrderItem


def get_order_by_id(order_id: str | UUID) -> Order | None:
    return Order.objects.select_related("customer").filter(id=order_id).first()


def get_order_for_customer(*, customer: User, order_id: str | UUID) -> Order | None:
    return Order.objects.select_related("customer").filter(id=order_id, customer=customer).first()


def get_orders_for_customer(
    *,
    customer: User,
    status: str | None = None,
    payment_status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> QuerySet[Order]:
    qs = Order.objects.filter(customer=customer)
    if status:
        qs = qs.filter(status=status)
    if payment_status:
        qs = qs.filter(payment_status=payment_status)
    if date_from:
        qs = qs.filter(created_at__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__lte=date_to)
    return qs.order_by("-created_at")


def get_orders_for_admin(
    *,
    status: str | None = None,
    payment_status: str | None = None,
    customer: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
) -> QuerySet[Order]:
    qs = Order.objects.select_related("customer").all()
    if status:
        qs = qs.filter(status=status)
    if payment_status:
        qs = qs.filter(payment_status=payment_status)
    if customer:
        qs = qs.filter(customer__id=customer)
    if date_from:
        qs = qs.filter(created_at__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__lte=date_to)
    if search:
        from django.db.models import Q

        qs = qs.filter(
            Q(order_number__icontains=search)
            | Q(customer__email__icontains=search)
            | Q(customer__first_name__icontains=search)
            | Q(customer__last_name__icontains=search)
        )
    return qs.order_by("-created_at")


def get_order_items(*, order: Order) -> QuerySet[OrderItem]:
    return order.items.select_related("product", "variant").all()
