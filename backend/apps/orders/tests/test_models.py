from __future__ import annotations

import pytest

from apps.orders.factories import OrderFactory, OrderItemFactory, OrderStatusHistoryFactory
from apps.orders.models import Order, OrderItem, OrderStatusHistory

pytestmark = pytest.mark.django_db


class TestOrderModel:
    def test_create_order(self):
        order = OrderFactory()
        assert Order.objects.count() == 1
        assert order.order_number.startswith("ORD-")

    def test_order_str(self):
        order = OrderFactory()
        assert str(order) == order.order_number


class TestOrderItemModel:
    def test_create_order_item(self):
        item = OrderItemFactory()
        assert OrderItem.objects.count() == 1
        assert item.line_total == item.unit_price * item.quantity

    def test_order_item_relation(self):
        order = OrderFactory()
        OrderItemFactory.create_batch(3, order=order)
        assert order.items.count() == 3


class TestOrderStatusHistoryModel:
    def test_create_status_history(self):
        history = OrderStatusHistoryFactory()
        assert OrderStatusHistory.objects.count() == 1
        assert str(history) == "None -> pending_payment"
