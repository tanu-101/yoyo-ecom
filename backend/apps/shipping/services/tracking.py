from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order
from apps.shipping.constants import TrackingStatus
from apps.shipping.models import OrderTracking


@transaction.atomic
def create_tracking(
    *,
    order: Order,
    carrier: str,
    tracking_number: str,
    tracking_url: str = "",
    estimated_delivery: str | None = None,
) -> OrderTracking:
    tracking, created = OrderTracking.objects.update_or_create(
        order=order,
        defaults={
            "carrier": carrier,
            "tracking_number": tracking_number,
            "tracking_url": tracking_url,
            "status": TrackingStatus.PROCESSING,
            "estimated_delivery": estimated_delivery,
            "last_update": timezone.now(),
        },
    )
    return tracking


@transaction.atomic
def update_tracking_status(
    *,
    tracking: OrderTracking,
    status: str,
) -> OrderTracking:
    tracking.status = status
    tracking.last_update = timezone.now()
    tracking.save(update_fields=["status", "last_update", "updated_at"])
    return tracking
