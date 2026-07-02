from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.payments.models import Payment


def get_payment_by_id(payment_id: str | UUID) -> Payment | None:
    return Payment.objects.select_related("order", "order__customer").filter(id=payment_id).first()


def get_payments_for_customer(*, customer: User) -> QuerySet[Payment]:
    return (
        Payment.objects.filter(order__customer=customer)
        .select_related("order")
        .order_by("-created_at")
    )


def get_payments_for_admin() -> QuerySet[Payment]:
    return Payment.objects.select_related("order", "order__customer").order_by("-created_at")
