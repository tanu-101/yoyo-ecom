from __future__ import annotations

from django.db.models import QuerySet

from apps.catalog.constants import ProductStatus
from apps.catalog.models import Category, Product


def get_active_products() -> QuerySet[Product]:
    return Product.objects.filter(status=ProductStatus.ACTIVE, deleted_at__isnull=True)


def get_product_by_slug(slug: str) -> Product | None:
    return Product.objects.filter(slug=slug, deleted_at__isnull=True).first()


def get_product_by_id(product_id: str) -> Product | None:
    return Product.objects.filter(id=product_id, deleted_at__isnull=True).first()


def get_categories() -> QuerySet[Category]:
    return Category.objects.filter(is_active=True, deleted_at__isnull=True)


def get_category_by_slug(slug: str) -> Category | None:
    return Category.objects.filter(slug=slug, is_active=True, deleted_at__isnull=True).first()
