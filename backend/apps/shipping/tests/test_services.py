from __future__ import annotations

import pytest

from apps.orders.factories import OrderFactory
from apps.shipping.constants import TrackingStatus
from apps.shipping.factories import OrderTrackingFactory
from apps.shipping.services.tracking import create_tracking, update_tracking_status

pytestmark = pytest.mark.django_db


class TestCreateTracking:
    def test_creates_tracking(self, customer_user):
        order = OrderFactory(customer=customer_user)

        tracking = create_tracking(
            order=order,
            carrier="FedEx",
            tracking_number="TRK123456789",
            tracking_url="https://fedex.com/track/TRK123456789",
        )

        assert tracking.order == order
        assert tracking.carrier == "FedEx"
        assert tracking.tracking_number == "TRK123456789"
        assert tracking.tracking_url == "https://fedex.com/track/TRK123456789"
        assert tracking.status == TrackingStatus.PROCESSING
        assert tracking.last_update is not None

    def test_updates_existing_tracking(self, customer_user):
        order = OrderFactory(customer=customer_user)

        tracking = create_tracking(
            order=order,
            carrier="FedEx",
            tracking_number="TRK123",
        )

        updated = create_tracking(
            order=order,
            carrier="UPS",
            tracking_number="TRK987",
        )

        assert updated.id == tracking.id
        assert updated.carrier == "UPS"
        assert updated.tracking_number == "TRK987"


class TestUpdateTrackingStatus:
    def test_updates_status(self):
        tracking = OrderTrackingFactory()

        result = update_tracking_status(tracking=tracking, status=TrackingStatus.IN_TRANSIT)

        result.refresh_from_db()
        assert result.status == TrackingStatus.IN_TRANSIT
        assert result.last_update is not None
