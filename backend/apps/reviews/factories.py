from __future__ import annotations

import factory

from apps.accounts.factories import CustomerUserFactory
from apps.catalog.factories import ProductFactory
from apps.orders.factories import OrderItemFactory
from apps.reviews.models import Review


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    product = factory.SubFactory(ProductFactory)
    customer = factory.SubFactory(CustomerUserFactory)
    order_item = factory.SubFactory(OrderItemFactory)
    rating = 5
    title = "Great product"
    content = "Highly recommended."
    status = "pending"
