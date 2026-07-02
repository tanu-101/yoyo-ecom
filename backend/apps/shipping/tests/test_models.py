from __future__ import annotations

import pytest

from apps.shipping.factories import OrderTrackingFactory, ShippingMethodFactory
from apps.shipping.models import OrderTracking, ShippingMethod

pytestmark = pytest.mark.django_db


class TestShippingMethod:
    def test_create_method(self):
        method = ShippingMethodFactory()
        assert ShippingMethod.objects.count() == 1
        assert str(method) == method.name


class TestOrderTracking:
    def test_create_tracking(self):
        tracking = OrderTrackingFactory()
        assert OrderTracking.objects.count() == 1
        assert str(tracking).startswith(tracking.carrier)
