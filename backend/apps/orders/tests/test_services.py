from __future__ import annotations

from decimal import Decimal

import pytest

from apps.carts.factories import CartFactory, CartItemFactory
from apps.carts.selectors.carts import get_cart_for_user
from apps.catalog.factories import VariantFactory
from apps.common.exceptions import BusinessRuleViolation
from apps.orders.factories import OrderFactory
from apps.orders.models import Order, OrderStatusHistory
from apps.orders.selectors.orders import get_order_items
from apps.orders.services.cancellation import cancel_order
from apps.orders.services.checkout import create_order_from_cart
from apps.orders.services.status_transitions import transition_order_status

pytestmark = pytest.mark.django_db


class TestCreateOrderFromCart:
    def test_creates_order_from_cart(self, customer_user):
        cart = CartFactory(customer=customer_user)
        variant = VariantFactory(stock_quantity=10)
        CartItemFactory(cart=cart, variant=variant, quantity=2, unit_price=variant.price)

        order = create_order_from_cart(
            customer=customer_user,
            shipping_cost=Decimal("10.00"),
            tax_amount=Decimal("5.00"),
        )

        assert Order.objects.count() == 1
        assert order.customer == customer_user
        assert order.status == "pending_payment"
        assert order.subtotal == Decimal(str(variant.price)) * 2
        assert order.shipping_cost == Decimal("10.00")
        assert order.tax_amount == Decimal("5.00")
        assert order.total_amount == order.subtotal + Decimal("10.00") + Decimal("5.00")

        # Verify order items
        items = get_order_items(order=order)
        assert items.count() == 1
        assert items[0].sku == variant.sku
        assert items[0].quantity == 2

        # Verify stock deducted
        variant.refresh_from_db()
        assert variant.stock_quantity == 8

        # Verify cart cleared
        cart = get_cart_for_user(user=customer_user)
        assert cart.items.count() == 0

        # Verify status history
        assert OrderStatusHistory.objects.filter(order=order).count() == 1

    def test_raises_error_on_empty_cart(self, customer_user):
        with pytest.raises(BusinessRuleViolation, match="Cart is empty"):
            create_order_from_cart(customer=customer_user)

    def test_raises_error_on_insufficient_stock(self, customer_user):
        cart = CartFactory(customer=customer_user)
        variant = VariantFactory(stock_quantity=1)
        CartItemFactory(cart=cart, variant=variant, quantity=5)

        with pytest.raises(BusinessRuleViolation, match="Insufficient stock"):
            create_order_from_cart(customer=customer_user)


class TestCancelOrder:
    def test_customer_cancels_before_shipped(self, customer_user):
        order = OrderFactory(customer=customer_user, status="pending_payment")
        result = cancel_order(order=order, cancelled_by=customer_user, reason="Changed mind")

        assert result.status == "cancelled"
        assert result.cancelled_by == customer_user
        assert result.cancellation_reason == "Changed mind"
        assert result.cancelled_at is not None

    def test_admin_cancels_processing_order(self, admin_user, customer_user):
        order = OrderFactory(customer=customer_user, status="processing")
        result = cancel_order(order=order, cancelled_by=admin_user, reason="Admin override")

        assert result.status == "cancelled"

    def test_cannot_cancel_delivered_order(self, customer_user):
        order = OrderFactory(customer=customer_user, status="delivered")

        with pytest.raises(BusinessRuleViolation, match="cannot be cancelled"):
            cancel_order(order=order, cancelled_by=customer_user)


class TestTransitionOrderStatus:
    def test_valid_transition(self, customer_user):
        order = OrderFactory(status="pending_payment")
        result = transition_order_status(
            order=order,
            to_status="placed",
            changed_by=customer_user,
            reason="Payment received",
        )

        assert result.status == "placed"
        assert result.placed_at is not None
        assert OrderStatusHistory.objects.filter(order=order).count() == 1

    def test_invalid_transition(self, customer_user):
        order = OrderFactory(status="pending_payment")

        with pytest.raises(BusinessRuleViolation, match="not allowed"):
            transition_order_status(
                order=order,
                to_status="shipped",
                changed_by=customer_user,
            )

    def test_transition_from_cancelled_fails(self, customer_user):
        order = OrderFactory(status="cancelled")

        with pytest.raises(BusinessRuleViolation, match="not allowed"):
            transition_order_status(
                order=order,
                to_status="processing",
                changed_by=customer_user,
            )
