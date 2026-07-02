from __future__ import annotations

from decimal import Decimal

import stripe
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.common.exceptions import BusinessRuleViolation
from apps.payments.constants import PaymentState, RefundState
from apps.payments.models import Payment, Refund


def _cents_from_decimal(amount: Decimal) -> int:
    return int(amount * 100)


def _decimal_from_cents(cents: int) -> Decimal:
    return Decimal(str(cents)) / Decimal("100")


@transaction.atomic
def process_refund(
    *,
    payment: Payment,
    amount: Decimal,
    reason: str = "",
    created_by: User | None = None,
    return_request_id: str | None = None,
) -> Refund:
    if payment.status != PaymentState.SUCCEEDED:
        raise BusinessRuleViolation(
            "Cannot refund a payment that was not successful.",
            code="payment_not_succeeded",
        )

    total_refunded = Decimal("0.00")
    for refund in payment.refunds.filter(status=RefundState.SUCCEEDED):
        total_refunded += refund.amount

    remaining = payment.amount - total_refunded
    if amount > remaining:
        raise BusinessRuleViolation(
            f"Refund amount exceeds remaining balance. Available: {remaining}.",
            code="refund_exceeds_balance",
        )

    stripe_refund = stripe.Refund.create(
        payment_intent=payment.provider_payment_intent_id,
        amount=_cents_from_decimal(amount),
        reason="requested_by_customer" if not reason else "duplicate",
        metadata={"return_request_id": return_request_id or ""},
    )

    refund = Refund.objects.create(
        payment=payment,
        order=payment.order,
        return_request_id=return_request_id,
        provider_refund_id=stripe_refund["id"],
        amount=amount,
        reason=reason,
        status=RefundState.SUCCEEDED,
        created_by=created_by,
        processed_at=timezone.now(),
    )

    order = payment.order
    total_refunded_after = total_refunded + amount
    if total_refunded_after >= order.total_amount:
        order.payment_status = "refunded"
    else:
        order.payment_status = "partially_refunded"
    order.save(update_fields=["payment_status", "updated_at"])

    return refund
