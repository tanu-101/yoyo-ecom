from __future__ import annotations

import factory

from apps.accounts.factories import CustomerUserFactory
from apps.catalog.factories import ProductFactory, VariantFactory
from apps.orders.constants import OrderStatus, PaymentStatus
from apps.orders.models import Order, OrderItem, OrderStatusHistory


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    order_number = factory.Sequence(lambda n: f"ORD-2026-{n + 1:06d}")
    customer = factory.SubFactory(CustomerUserFactory)
    status = OrderStatus.PENDING_PAYMENT
    payment_status = PaymentStatus.PENDING
    subtotal = 100.00
    discount_amount = 0.00
    shipping_cost = 10.00
    tax_amount = 5.00
    total_amount = 115.00


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    variant = factory.SubFactory(VariantFactory)
    product_name = factory.SelfAttribute("product.name")
    variant_name = factory.SelfAttribute("variant.name")
    sku = factory.SelfAttribute("variant.sku")
    quantity = 1
    unit_price = 99.99
    line_total = 99.99


class OrderStatusHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderStatusHistory

    order = factory.SubFactory(OrderFactory)
    from_status = None
    to_status = OrderStatus.PENDING_PAYMENT
    reason = "Order created."
