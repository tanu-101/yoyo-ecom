from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.returns.models import ReturnRequest


def get_return_by_id(return_id: str | UUID) -> ReturnRequest | None:
    return ReturnRequest.objects.select_related("order", "customer").filter(id=return_id).first()


def get_returns_for_customer(*, customer: User) -> QuerySet[ReturnRequest]:
    return ReturnRequest.objects.filter(customer=customer).order_by("-created_at")


def get_returns_for_admin() -> QuerySet[ReturnRequest]:
    return ReturnRequest.objects.select_related("order", "customer").order_by("-created_at")
