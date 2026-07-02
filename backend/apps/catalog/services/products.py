from __future__ import annotations

from django.db import transaction
from django.utils.text import slugify

from apps.accounts.models import User
from apps.catalog.models import Category, Product


@transaction.atomic
def create_category(
    *,
    name: str,
    slug: str | None = None,
    description: str = "",
    parent: Category | None = None,
    image: str = "",
    is_active: bool = True,
    sort_order: int = 0,
) -> Category:
    if not slug:
        slug = slugify(name)

    return Category.objects.create(
        name=name,
        slug=slug,
        description=description,
        parent=parent,
        image=image,
        is_active=is_active,
        sort_order=sort_order,
    )


@transaction.atomic
def create_product(
    *,
    category: Category,
    name: str,
    description: str,
    base_price: float,
    slug: str | None = None,
    status: str = "draft",
    is_featured: bool = False,
    created_by: User | None = None,
) -> Product:
    if not slug:
        slug = slugify(name)

    return Product.objects.create(
        category=category,
        name=name,
        slug=slug,
        description=description,
        base_price=base_price,
        status=status,
        is_featured=is_featured,
        created_by=created_by,
    )


@transaction.atomic
def update_product(
    *,
    product: Product,
    data: dict,
) -> Product:
    for field, value in data.items():
        setattr(product, field, value)

    product.save()
    return product
