import pytest

from apps.catalog.constants import ProductStatus
from apps.catalog.models import Category, Product


@pytest.mark.django_db
def test_create_category():
    category = Category.objects.create(name="Electronics", slug="electronics")
    assert category.name == "Electronics"
    assert category.slug == "electronics"
    assert str(category) == "Electronics"


@pytest.mark.django_db
def test_create_product(user_factory):
    category = Category.objects.create(name="Electronics", slug="electronics")
    user = user_factory()
    product = Product.objects.create(
        category=category,
        name="Smartphone",
        slug="smartphone",
        description="A great smartphone",
        base_price=999.99,
        created_by=user,
    )
    assert product.name == "Smartphone"
    assert product.category == category
    assert product.status == ProductStatus.DRAFT
    assert str(product) == "Smartphone"
