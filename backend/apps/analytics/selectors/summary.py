from __future__ import annotations

from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek

from apps.orders.constants import PaymentStatus
from apps.orders.models import Order, OrderItem


def get_summary() -> dict:
    paid_statuses = [PaymentStatus.PAID, PaymentStatus.PARTIALLY_REFUNDED, PaymentStatus.REFUNDED]

    total_orders = Order.objects.filter(
        ~Q(status="cancelled"),
    ).count()

    revenue_data = Order.objects.filter(
        payment_status__in=paid_statuses,
    ).aggregate(
        total_revenue=Sum("total_amount"),
    )

    total_revenue = revenue_data["total_revenue"] or Decimal("0.00")

    paid_orders = Order.objects.filter(
        payment_status__in=paid_statuses,
    ).count()

    avg_order_value = total_revenue / paid_orders if paid_orders else Decimal("0.00")

    total_cancelled = Order.objects.filter(status="cancelled").count()
    total_fulfilled = total_orders + total_cancelled
    return_rate = Decimal("0.00")
    if total_fulfilled > 0:
        from apps.returns.models import ReturnRequest

        total_returns = ReturnRequest.objects.count()
        return_rate = (Decimal(str(total_returns)) / Decimal(str(total_fulfilled))) * Decimal("100")

    return {
        "total_orders": total_orders,
        "total_revenue": str(total_revenue),
        "average_order_value": str(avg_order_value),
        "return_rate": str(return_rate.quantize(Decimal("0.01"))),
    }


def get_sales_data(
    *, date_from: str | None = None, date_to: str | None = None, group_by: str = "day"
) -> list:
    qs = Order.objects.filter(
        ~Q(status="cancelled"),
    )

    if date_from:
        qs = qs.filter(created_at__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__lte=date_to)

    trunc_func = {
        "day": TruncDay,
        "week": TruncWeek,
        "month": TruncMonth,
    }.get(group_by, TruncDay)

    return list(
        qs.annotate(
            period=trunc_func("created_at"),
        )
        .values("period")
        .annotate(
            order_count=Count("id"),
            revenue=Sum("total_amount"),
        )
        .order_by("period")
    )


def get_top_products(
    *, limit: int = 10, date_from: str | None = None, date_to: str | None = None
) -> list:
    qs = (
        OrderItem.objects.select_related("product", "variant")
        .values(
            "product__id",
            "product__name",
        )
        .annotate(
            total_quantity=Sum("quantity"),
            total_revenue=Sum("line_total"),
        )
        .order_by("-total_quantity")[:limit]
    )

    return list(qs)


def get_return_rate(*, date_from: str | None = None, date_to: str | None = None) -> dict:
    from apps.returns.models import ReturnRequest

    orders_qs = Order.objects.all()
    returns_qs = ReturnRequest.objects.all()

    if date_from:
        orders_qs = orders_qs.filter(created_at__gte=date_from)
        returns_qs = returns_qs.filter(created_at__gte=date_from)
    if date_to:
        orders_qs = orders_qs.filter(created_at__lte=date_to)
        returns_qs = returns_qs.filter(created_at__lte=date_to)

    total_orders = orders_qs.count()
    total_returns = returns_qs.count()

    rate = Decimal("0.00")
    if total_orders > 0:
        rate = (Decimal(str(total_returns)) / Decimal(str(total_orders))) * Decimal("100")

    return {
        "total_orders": total_orders,
        "total_returns": total_returns,
        "return_rate": str(rate.quantize(Decimal("0.01"))),
    }
