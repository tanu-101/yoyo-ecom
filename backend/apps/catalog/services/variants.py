from __future__ import annotations

from django.db import transaction

from apps.catalog.models import (
    Product,
    Variant,
    VariantAttribute,
    VariantAttributeValue,
    VariantOption,
)


@transaction.atomic
def create_variant(
    *,
    product: Product,
    sku: str,
    name: str,
    price: float,
    stock_quantity: int = 0,
    status: str = "active",
    image: str = "",
) -> Variant:
    return Variant.objects.create(
        product=product,
        sku=sku,
        name=name,
        price=price,
        stock_quantity=stock_quantity,
        status=status,
        image=image,
    )


@transaction.atomic
def add_attribute_to_variant(
    *,
    variant: Variant,
    attribute: VariantAttribute,
    value: VariantAttributeValue,
) -> VariantOption:
    return VariantOption.objects.create(
        variant=variant,
        attribute=attribute,
        value=value,
    )
