# Model Conventions

## Base Models

Always inherit from base models in `apps/common/models/base.py`:

```python
from apps.common.models.base import UUIDModel, TimeStampedModel, SoftDeleteModel

class MyModel(UUIDModel, TimeStampedModel, SoftDeleteModel):
    # Your fields here
```

### Available Base Models

| Model | Fields | Purpose |
|-------|--------|---------|
| `UUIDModel` | `id` (UUID) | Unique identifier, not guessable |
| `TimeStampedModel` | `created_at`, `updated_at` | Track creation and modification |
| `SoftDeleteModel` | `is_deleted`, `deleted_at` | Soft delete instead of hard delete |

## Model Design Patterns

### Product Models

```python
from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator

from apps.common.models.base import UUIDModel, TimeStampedModel, SoftDeleteModel

class Category(UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(UUIDModel, TimeStampedModel, SoftDeleteModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    sku = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    track_inventory = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_deleted']),
        ]

    def __str__(self):
        return self.name
```

### User/Roles Models

```python
from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.common.models.base import UUIDModel

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # ...

    def create_superuser(self, email, password, **extra_fields):
        # ...

class User(UUIDModel, AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STAFF = 'staff', 'Staff'
        CUSTOMER = 'customer', 'Customer'

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
```

### Order Models

```python
from __future__ import annotations

from django.db import models

from apps.common.models.base import UUIDModel, TimeStampedModel
from apps.accounts.models import User

class Order(UUIDModel, TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_address = models.JSONField()
    billing_address = models.JSONField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id}"
```

## Field Types

### Common Field Types

| Field | Use Case |
|-------|----------|
| `CharField` | Short text (max_length required) |
| `TextField` | Long text, descriptions |
| `EmailField` | Email addresses |
| `URLField` | URLs |
| `SlugField` | URL-safe strings |
| `PositiveIntegerField` | Counts, quantities |
| `DecimalField` | Money, precise decimals (price, amount) |
| `BooleanField` | Flags, toggles |
| `DateField` | Dates |
| `DateTimeField` | Timestamps |
| `UUIDField` | Unique identifiers |
| `JSONField` | Structured data, addresses |
| `ForeignKey` | Many-to-one relationships |
| `OneToOneField` | One-to-one relationships |
| `ManyToManyField` | Many-to-many relationships |

### Field Validators

```python
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    RegexValidator,
    URLValidator,
)

price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    validators=[MinValueValidator(Decimal('0.01'))]
)

phone = models.CharField(
    validators=[
        RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in format: '+999999999'"
        )
    ]
)
```

## Model Managers

### Custom QuerySet and Manager

```python
from django.db import models

class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, is_deleted=False)

    def in_category(self, category):
        return self.filter(category=category)

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

class Product(UUIDModel, TimeStampedModel):
    # ... fields ...
    objects = ProductManager()
```

## Indexes

Add indexes for frequently queried fields:

```python
class Meta:
    indexes = [
        models.Index(fields=['slug']),
        models.Index(fields=['is_active', 'created_at']),
        models.Index(fields=['user', '-created_at']),
    ]
```

## Model Methods

```python
def __str__(self):
    return self.name

@property
def display_name(self):
    return f"{self.first_name} {self.last_name}"

def get_absolute_url(self):
    return f'/products/{self.slug}/'
```

## Model Signals

Use signals sparingly. Prefer service layer for business logic.

```python
# apps/products/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.products.models import Product

@receiver(post_save, sender=Product)
def product_created(sender, instance, created, **kwargs):
    if created:
        # Do something
        pass
```

## Best Practices

1. **Use UUIDs for primary keys** - Not guessable, safe for URLs
2. **Use soft delete** - Don't hard delete user data, orders, products
3. **Add indexes** - For fields used in filters and queries
4. **Use validators** - Validate at model level
5. **Define `__str__`** - Always return a readable string
6. **Use proper on_delete** - PROTECT, CASCADE, SET_NULL, SET_DEFAULT
7. **Use verbose_name** - For user-facing labels
8. **Group related fields** - Use comments to separate field groups