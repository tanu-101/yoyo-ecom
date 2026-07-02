from __future__ import annotations

from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.accounts.constants import UserRole
from apps.common.models.base import SoftDeleteModel


class User(AbstractUser, SoftDeleteModel):
    username: models.CharField = models.CharField(max_length=150, blank=True, default="")
    email: models.EmailField = models.EmailField(unique=True)
    role: models.CharField = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER
    )
    phone: models.CharField = models.CharField(max_length=32, blank=True)
    profile_picture: models.URLField = models.URLField(blank=True)
    is_email_verified: models.BooleanField = models.BooleanField(default=False)
    is_phone_verified: models.BooleanField = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    @property
    def is_admin_role(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_staff_role(self) -> bool:
        return self.role == UserRole.STAFF

    @property
    def is_customer_role(self) -> bool:
        return self.role == UserRole.CUSTOMER
