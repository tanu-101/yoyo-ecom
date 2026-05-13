from __future__ import annotations

from django.db import transaction

from apps.accounts.models import Address, User


@transaction.atomic
def create_address(*, user: User, data: dict) -> Address:
    address = Address.objects.create(user=user, **data)
    if address.is_default:
        set_default_address(user=user, address=address)
    return address


@transaction.atomic
def update_address(*, user: User, address: Address, data: dict) -> Address:
    for field, value in data.items():
        setattr(address, field, value)
    address.save()
    if address.is_default:
        set_default_address(user=user, address=address)
    return address


@transaction.atomic
def delete_address(*, user: User, address: Address) -> None:
    address.soft_delete()


@transaction.atomic
def set_default_address(*, user: User, address: Address) -> Address:
    Address.objects.filter(user=user, deleted_at__isnull=True, is_default=True).exclude(
        id=address.id
    ).update(is_default=False)
    address.is_default = True
    address.save(update_fields=["is_default", "updated_at"])
    return address
