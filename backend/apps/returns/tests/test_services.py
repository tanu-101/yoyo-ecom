from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.common.exceptions import BusinessRuleViolation
from apps.orders.constants import OrderStatus
from apps.orders.factories import OrderFactory, OrderItemFactory
from apps.returns.factories import ReturnItemFactory, ReturnRequestFactory
from apps.returns.models import ReturnStatus, ReturnStatusHistory
from apps.returns.services.approval import approve_return, reject_return
from apps.returns.services.eligibility import (
    RETURN_WINDOW_DAYS,
    validate_return_eligibility,
    validate_return_quantity,
)
from apps.returns.services.processing import mark_received, process_return

pytestmark = pytest.mark.django_db


class TestValidateReturnEligibility:
    def test_valid_eligibility(self, customer_user):
        order = OrderFactory(
            customer=customer_user,
            status=OrderStatus.DELIVERED,
            delivered_at=timezone.now(),
        )

        validate_return_eligibility(customer=customer_user, order=order)

    def test_raises_on_not_customer_order(self, customer_user, admin_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.DELIVERED)

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_return_eligibility(customer=admin_user, order=order)

        assert exc.value.code == "permission_denied"

    def test_raises_on_not_delivered(self, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.SHIPPED)

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_return_eligibility(customer=customer_user, order=order)

        assert exc.value.code == "return_not_eligible"

    def test_raises_on_expired_window(self, customer_user):
        order = OrderFactory(
            customer=customer_user,
            status=OrderStatus.DELIVERED,
            delivered_at=timezone.now() - timedelta(days=RETURN_WINDOW_DAYS + 1),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_return_eligibility(customer=customer_user, order=order)

        assert exc.value.code == "return_window_expired"


class TestValidateReturnQuantity:
    def test_valid_quantity(self, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.DELIVERED)
        order_item = OrderItemFactory(order=order, quantity=3)

        validate_return_quantity(
            order=order,
            items_data=[{"order_item": order_item.id, "quantity": 2}],
        )

    def test_raises_on_invalid_order_item(self, customer_user):
        order = OrderFactory(customer=customer_user)

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_return_quantity(
                order=order,
                items_data=[{"order_item": "00000000-0000-0000-0000-000000000000", "quantity": 1}],
            )

        assert exc.value.code == "invalid_order_item"

    def test_raises_on_zero_quantity(self, customer_user):
        order = OrderFactory(customer=customer_user)
        order_item = OrderItemFactory(order=order, quantity=3)

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_return_quantity(
                order=order,
                items_data=[{"order_item": order_item.id, "quantity": 0}],
            )

        assert exc.value.code == "invalid_quantity"

    def test_raises_on_quantity_exceeds_purchased(self, customer_user):
        order = OrderFactory(customer=customer_user)
        order_item = OrderItemFactory(order=order, quantity=2)

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_return_quantity(
                order=order,
                items_data=[{"order_item": order_item.id, "quantity": 5}],
            )

        assert exc.value.code == "invalid_quantity"

    def test_raises_on_duplicate_return(self, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.DELIVERED)
        order_item = OrderItemFactory(order=order, quantity=3)
        return_request = ReturnRequestFactory(
            order=order,
            customer=customer_user,
            status="pending_review",
        )
        ReturnItemFactory(return_request=return_request, order_item=order_item, quantity=1)

        with pytest.raises(BusinessRuleViolation) as exc:
            validate_return_quantity(
                order=order,
                items_data=[{"order_item": order_item.id, "quantity": 1}],
            )

        assert exc.value.code == "duplicate_return"


class TestApproveReturn:
    def test_approves_pending_return(self, admin_user, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.DELIVERED)
        return_request = ReturnRequestFactory(
            order=order,
            customer=customer_user,
            status="pending_review",
        )

        result = approve_return(
            return_request=return_request,
            reviewed_by=admin_user,
            resolution="refund",
            refund_amount=Decimal("99.99"),
            admin_notes="Approved - item defective",
        )

        result.refresh_from_db()
        assert result.status == ReturnStatus.APPROVED
        assert result.resolution == "refund"
        assert result.refund_amount == Decimal("99.99")
        assert result.admin_notes == "Approved - item defective"
        assert result.reviewed_by == admin_user
        assert result.reviewed_at is not None
        assert ReturnStatusHistory.objects.filter(return_request=result).count() == 1

    def test_raises_on_non_pending_return(self, admin_user):
        return_request = ReturnRequestFactory(status="approved")

        with pytest.raises(BusinessRuleViolation) as exc:
            approve_return(
                return_request=return_request, reviewed_by=admin_user, resolution="refund"
            )

        assert exc.value.code == "invalid_return_status"


class TestRejectReturn:
    def test_rejects_pending_return(self, admin_user, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.DELIVERED)
        return_request = ReturnRequestFactory(
            order=order,
            customer=customer_user,
            status="pending_review",
        )

        result = reject_return(
            return_request=return_request,
            reviewed_by=admin_user,
            rejection_reason="Item not defective",
            admin_notes="Tested and works fine",
        )

        result.refresh_from_db()
        assert result.status == ReturnStatus.REJECTED
        assert result.rejection_reason == "Item not defective"
        assert result.admin_notes == "Tested and works fine"
        assert result.reviewed_by == admin_user
        assert result.reviewed_at is not None
        assert ReturnStatusHistory.objects.filter(return_request=result).count() == 1

    def test_raises_on_non_pending_return(self, admin_user):
        return_request = ReturnRequestFactory(status="approved")

        with pytest.raises(BusinessRuleViolation) as exc:
            reject_return(return_request=return_request, reviewed_by=admin_user)

        assert exc.value.code == "invalid_return_status"


class TestMarkReceived:
    def test_marks_approved_return_as_received(self, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.DELIVERED)
        return_request = ReturnRequestFactory(
            order=order,
            customer=customer_user,
            status="approved",
        )

        result = mark_received(return_request=return_request)

        result.refresh_from_db()
        assert result.status == ReturnStatus.RECEIVED
        assert result.received_at is not None
        assert ReturnStatusHistory.objects.filter(return_request=result).count() == 1

    def test_marks_in_transit_return_as_received(self, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.DELIVERED)
        return_request = ReturnRequestFactory(
            order=order,
            customer=customer_user,
            status="in_transit",
        )

        result = mark_received(return_request=return_request)

        result.refresh_from_db()
        assert result.status == ReturnStatus.RECEIVED

    def test_raises_on_pending_review_status(self, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.DELIVERED)
        return_request = ReturnRequestFactory(
            order=order,
            customer=customer_user,
            status="pending_review",
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            mark_received(return_request=return_request)

        assert exc.value.code == "invalid_return_status"


class TestProcessReturn:
    def test_processes_refund_return_and_restocks(self, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.DELIVERED)
        order_item = OrderItemFactory(order=order, quantity=2)
        variant = order_item.variant
        initial_stock = variant.stock_quantity

        return_request = ReturnRequestFactory(
            order=order,
            customer=customer_user,
            status="received",
            resolution="refund",
        )
        ReturnItemFactory(return_request=return_request, order_item=order_item, quantity=2)

        result = process_return(return_request=return_request)

        result.refresh_from_db()
        assert result.status == ReturnStatus.REFUNDED
        assert result.completed_at is not None

        variant.refresh_from_db()
        assert variant.stock_quantity == initial_stock + 2
        assert ReturnStatusHistory.objects.filter(return_request=result).count() == 1

    def test_raises_if_not_received(self, customer_user):
        order = OrderFactory(customer=customer_user, status=OrderStatus.DELIVERED)
        return_request = ReturnRequestFactory(
            order=order,
            customer=customer_user,
            status="approved",
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            process_return(return_request=return_request)

        assert exc.value.code == "invalid_return_status"
