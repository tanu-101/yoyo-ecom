from __future__ import annotations

import factory

from apps.catalog.constants import ProductStatus, VariantStatus
from apps.catalog.models import Category, Product, Variant


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")
    is_active = True
    sort_order = 0


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    description = "A test product."
    base_price = factory.LazyFunction(lambda: "99.99")
    status = ProductStatus.ACTIVE
    is_featured = False


class VariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Variant

    product = factory.SubFactory(ProductFactory)
    sku = factory.Sequence(lambda n: f"SKU-{n:05d}")
    name = factory.Sequence(lambda n: f"Variant {n}")
    price = factory.LazyFunction(lambda: "99.99")
    stock_quantity = 10
    status = VariantStatus.ACTIVE
    image = ""
