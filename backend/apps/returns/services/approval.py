from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.common.exceptions import BusinessRuleViolation
from apps.returns.models import ReturnRequest, ReturnStatus
from apps.returns.models.status_history import ReturnStatusHistory


@transaction.atomic
def approve_return(
    *,
    return_request: ReturnRequest,
    reviewed_by: User,
    resolution: str,
    refund_amount: Decimal | None = None,
    admin_notes: str = "",
) -> ReturnRequest:
    if return_request.status != ReturnStatus.PENDING_REVIEW:
        raise BusinessRuleViolation(
            "Only pending review returns can be approved.",
            code="invalid_return_status",
        )

    previous_status = return_request.status
    return_request.status = ReturnStatus.APPROVED
    return_request.resolution = resolution
    return_request.refund_amount = refund_amount
    return_request.admin_notes = admin_notes or return_request.admin_notes
    return_request.reviewed_by = reviewed_by
    return_request.reviewed_at = timezone.now()
    return_request.save(
        update_fields=[
            "status",
            "resolution",
            "refund_amount",
            "admin_notes",
            "reviewed_by",
            "reviewed_at",
            "updated_at",
        ]
    )

    ReturnStatusHistory.objects.create(
        return_request=return_request,
        from_status=previous_status,
        to_status=ReturnStatus.APPROVED,
        changed_by=reviewed_by,
        reason=admin_notes or "Return approved.",
    )

    return return_request


@transaction.atomic
def reject_return(
    *,
    return_request: ReturnRequest,
    reviewed_by: User,
    rejection_reason: str = "",
    admin_notes: str = "",
) -> ReturnRequest:
    if return_request.status != ReturnStatus.PENDING_REVIEW:
        raise BusinessRuleViolation(
            "Only pending review returns can be rejected.",
            code="invalid_return_status",
        )

    previous_status = return_request.status
    return_request.status = ReturnStatus.REJECTED
    return_request.rejection_reason = rejection_reason
    return_request.admin_notes = admin_notes or return_request.admin_notes
    return_request.reviewed_by = reviewed_by
    return_request.reviewed_at = timezone.now()
    return_request.save(
        update_fields=[
            "status",
            "rejection_reason",
            "admin_notes",
            "reviewed_by",
            "reviewed_at",
            "updated_at",
        ]
    )

    ReturnStatusHistory.objects.create(
        return_request=return_request,
        from_status=previous_status,
        to_status=ReturnStatus.REJECTED,
        changed_by=reviewed_by,
        reason=rejection_reason or "Return rejected.",
    )

    return return_request
