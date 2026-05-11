from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.accounts.constants import UserRole


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER)
    phone = models.CharField(max_length=32, blank=True)
    profile_picture = models.URLField(blank=True)
    is_email_verified = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

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

