from __future__ import annotations

from decimal import Decimal

import pytest

from apps.analytics.selectors.summary import (
    get_return_rate,
    get_sales_data,
    get_summary,
    get_top_products,
)
from apps.catalog.factories import ProductFactory, VariantFactory
from apps.orders.constants import OrderStatus, PaymentStatus
from apps.orders.factories import OrderFactory, OrderItemFactory


@pytest.mark.django_db
class TestGetSummary:
    def test_returns_empty_summary_when_no_orders(self):
        result = get_summary()
        assert result["total_orders"] == 0
        assert result["total_revenue"] == "0.00"
        assert result["average_order_value"] == "0.00"

    def test_returns_summary_with_orders(self):
        OrderFactory(
            status=OrderStatus.DELIVERED,
            payment_status=PaymentStatus.PAID,
            total_amount="100.00",
        )
        result = get_summary()
        assert result["total_orders"] >= 1
        assert Decimal(result["total_revenue"]) >= Decimal("100.00")

    def test_summary_excludes_cancelled_orders_from_total(self):
        OrderFactory(status=OrderStatus.CANCELLED)
        result = get_summary()
        assert result["total_revenue"] == "0.00"


@pytest.mark.django_db
class TestGetSalesData:
    def test_returns_empty_when_no_orders(self):
        data = get_sales_data()
        assert data == []

    def test_returns_grouped_sales_data(self):
        OrderFactory(
            status=OrderStatus.DELIVERED,
            payment_status=PaymentStatus.PAID,
            total_amount="50.00",
        )
        data = get_sales_data()
        assert len(data) >= 1
        assert data[0]["revenue"] is not None


@pytest.mark.django_db
class TestGetTopProducts:
    def test_returns_empty_when_no_order_items(self):
        products = get_top_products()
        assert products == []

    def test_returns_top_products(self):
        product = ProductFactory()
        variant = VariantFactory(product=product, price="25.00")
        order = OrderFactory()
        OrderItemFactory(
            order=order,
            product=product,
            variant=variant,
            quantity=5,
            unit_price="25.00",
            line_total="125.00",
        )
        products = get_top_products()
        assert len(products) >= 1
        assert products[0]["total_quantity"] >= 5


@pytest.mark.django_db
class TestGetReturnRate:
    def test_returns_zero_when_no_orders(self):
        result = get_return_rate()
        assert result["total_orders"] == 0
        assert result["total_returns"] == 0

    def test_returns_return_rate(self):
        OrderFactory()
        result = get_return_rate()
        assert result["total_orders"] >= 1
        assert result["return_rate"] == "0.00"
