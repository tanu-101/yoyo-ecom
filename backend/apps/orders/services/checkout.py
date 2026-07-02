from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.carts.models.cart import Cart
from apps.carts.selectors.carts import calculate_cart_totals, get_cart_items
from apps.carts.services.carts import clear_cart
from apps.common.exceptions import BusinessRuleViolation
from apps.inventory.constants import InventoryTransactionType
from apps.inventory.services.stock_adjustments import adjust_stock
from apps.orders.constants import OrderStatus, PaymentStatus
from apps.orders.models import Order, OrderItem, OrderStatusHistory


def _generate_order_number() -> str:
    year = timezone.now().year
    last = Order.objects.select_for_update().order_by("-created_at").first()
    if last and last.order_number:
        last_num = int(last.order_number.split("-")[-1])
        next_num = last_num + 1
    else:
        next_num = 1
    return f"ORD-{year}-{next_num:06d}"


@transaction.atomic
def create_order_from_cart(
    *,
    customer: User,
    shipping_cost: Decimal = Decimal("0.00"),
    tax_amount: Decimal = Decimal("0.00"),
    customer_notes: str = "",
    discount_amount: Decimal = Decimal("0.00"),
) -> Order:
    cart = Cart.objects.select_for_update().filter(customer=customer).first()
    if not cart:
        raise BusinessRuleViolation("Cart is empty.", code="cart_empty")

    cart_items = list(get_cart_items(cart=cart))
    if not cart_items:
        raise BusinessRuleViolation("Cart is empty.", code="cart_empty")

    totals = calculate_cart_totals(cart=cart)
    subtotal = totals["subtotal"]
    total = subtotal + shipping_cost + tax_amount - discount_amount
    if total < Decimal("0.00"):
        total = Decimal("0.00")

    order_number = _generate_order_number()

    order = Order.objects.create(
        order_number=order_number,
        customer=customer,
        status=OrderStatus.PENDING_PAYMENT,
        payment_status=PaymentStatus.PENDING,
        subtotal=subtotal,
        discount_amount=discount_amount,
        shipping_cost=shipping_cost,
        tax_amount=tax_amount,
        total_amount=total,
        customer_notes=customer_notes,
    )

    order_items = []
    for cart_item in cart_items:
        variant = cart_item.variant
        locked_variant = type(variant).objects.select_for_update().get(id=variant.id)

        if locked_variant.status != "active" or locked_variant.deleted_at is not None:
            raise BusinessRuleViolation(
                f"Variant '{locked_variant.sku}' is no longer available.",
                code="variant_unavailable",
            )

        if locked_variant.stock_quantity < cart_item.quantity:
            raise BusinessRuleViolation(
                f"Insufficient stock for '{locked_variant.sku}'. "
                f"Available: {locked_variant.stock_quantity}.",
                code="insufficient_stock",
            )

        line_total = cart_item.unit_price * cart_item.quantity

        item = OrderItem(
            order=order,
            product=cart_item.product,
            variant=locked_variant,
            product_name=cart_item.product.name,
            variant_name=locked_variant.name,
            sku=locked_variant.sku,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            line_total=line_total,
        )
        order_items.append(item)

        adjust_stock(
            variant=locked_variant,
            quantity_changed=-cart_item.quantity,
            transaction_type=InventoryTransactionType.ORDER_PLACED,
            reference_type="order",
            reference_id=order.id,
            notes=f"Order {order_number} checkout",
        )

    OrderItem.objects.bulk_create(order_items)

    OrderStatusHistory.objects.create(
        order=order,
        from_status=None,
        to_status=OrderStatus.PENDING_PAYMENT,
        changed_by=customer,
        reason="Order created from cart.",
    )

    clear_cart(user=customer)

    from apps.notifications.services.dispatch import dispatch_order_notifications

    dispatch_order_notifications(
        user=customer,
        notification_type="order_confirmation",
        subject=f"Order {order.order_number} confirmed",
        body=f"Your order {order.order_number} has been placed successfully. "
        f"Total: ${order.total_amount:.2f}. Please complete payment to proceed.",
    )

    return order
