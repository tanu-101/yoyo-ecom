from __future__ import annotations

from decimal import Decimal

import pytest

from apps.catalog.constants import ProductStatus, VariantStatus
from apps.catalog.factories import CategoryFactory, ProductFactory
from apps.catalog.models import VariantAttribute, VariantAttributeValue, VariantOption
from apps.catalog.services.products import create_category, create_product, update_product
from apps.catalog.services.variants import add_attribute_to_variant, create_variant

pytestmark = pytest.mark.django_db


class TestCreateCategory:
    def test_creates_category(self):
        category = create_category(name="Electronics", description="Electronic items")

        assert category.name == "Electronics"
        assert category.slug == "electronics"
        assert category.description == "Electronic items"
        assert category.is_active is True

    def test_creates_category_with_custom_slug(self):
        category = create_category(name="Electronics", slug="electronics-category")

        assert category.slug == "electronics-category"


class TestCreateProduct:
    def test_creates_product(self, customer_user):
        category = CategoryFactory()

        product = create_product(
            category=category,
            name="Test Product",
            description="A test product",
            base_price=99.99,
            created_by=customer_user,
        )

        assert product.name == "Test Product"
        assert product.slug == "test-product"
        assert product.description == "A test product"
        assert product.base_price == 99.99
        assert product.status == ProductStatus.DRAFT
        assert product.created_by == customer_user

    def test_creates_product_with_custom_slug(self):
        category = CategoryFactory()

        product = create_product(
            category=category,
            name="Test Product",
            description="A test product",
            base_price=99.99,
            slug="custom-slug",
        )

        assert product.slug == "custom-slug"


class TestUpdateProduct:
    def test_updates_product_fields(self):
        product = ProductFactory()

        updated = update_product(
            product=product,
            data={"name": "Updated Name", "base_price": 149.99, "is_featured": True},
        )

        updated.refresh_from_db()
        assert updated.name == "Updated Name"
        assert updated.base_price == Decimal("149.99")
        assert updated.is_featured is True


class TestCreateVariant:
    def test_creates_variant(self):
        product = ProductFactory()

        variant = create_variant(
            product=product,
            sku="SKU-TEST-001",
            name="Large",
            price=129.99,
            stock_quantity=20,
            status=VariantStatus.ACTIVE,
        )

        assert variant.product == product
        assert variant.sku == "SKU-TEST-001"
        assert variant.name == "Large"
        assert variant.price == 129.99
        assert variant.stock_quantity == 20
        assert variant.status == VariantStatus.ACTIVE


class TestAddAttributeToVariant:
    def test_adds_attribute_to_variant(self):
        product = ProductFactory()
        variant = create_variant(product=product, sku="SKU-ATTR", name="Test", price=10.00)

        attr = VariantAttribute.objects.create(name="Size", slug="size")
        value = VariantAttributeValue.objects.create(attribute=attr, value="Large", slug="large")

        option = add_attribute_to_variant(variant=variant, attribute=attr, value=value)

        assert option.variant == variant
        assert option.attribute == attr
        assert option.value == value
        assert VariantOption.objects.filter(variant=variant).count() == 1
