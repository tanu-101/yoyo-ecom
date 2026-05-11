# Django Backend Patterns

## Django Project Structure

```
backend/
├── config/                 # Django settings package
│   ├── settings/
│   │   ├── base.py        # Base settings (imports, installed apps, middleware)
│   │   ├── local.py       # Local development
│   │   ├── production.py  # Production (uses environment variables)
│   │   └── test.py        # Testing configuration
│   ├── urls.py           # Root URL configuration
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
├── apps/                  # Django apps
│   ├── common/           # Shared utilities
│   ├── accounts/         # User authentication
│   └── [other apps]/
├── manage.py
└── pyproject.toml         # Dependencies and tool config
```

## App Structure

Each Django app should follow this structure:

```python
apps/<app_name>/
├── __init__.py
├── models/
│   └── __init__.py
│   └── [model files]
├── selectors/
│   └── __init__.py
│   └── [selector files]
├── services/
│   └── __init__.py
│   └── [service files]
├── views/
│   └── __init__.py
│   └── [view files]
├── serializers/
│   └── __init__.py
│   └── [serializer files]
├── urls.py
└── admin.py
```

## Base Models

Always inherit from base models in `apps/common/models/base.py`:

```python
from apps.common.models.base import UUIDModel, TimeStampedModel, SoftDeleteModel

class Product(UUIDModel, TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

### UUIDModel
- Provides UUID primary key (`id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`)

### TimeStampedModel
- Adds `created_at` and `updated_at` fields with auto_now_add and auto_now

### SoftDeleteModel
- Adds `is_deleted` boolean and `deleted_at` datetime
- Use `objects` manager (excludes deleted), `all_objects` (includes all)
- Override `delete()` to soft delete

## Services Pattern

Business logic goes in services. Views should be thin.

```python
# apps/products/services/product_service.py
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.products.models import Product

class ProductService:
    @staticmethod
    def create_product(name: str, price: Decimal) -> Product:
        from apps.products.models import Product
        return Product.objects.create(name=name, price=price)

    @staticmethod
    def update_price(product: Product, new_price: Decimal) -> Product:
        product.price = new_price
        product.save(update_fields=['price', 'updated_at'])
        return product
```

## Selectors Pattern

Query logic goes in selectors.

```python
# apps/products/selectors/product_selector.py
from __future__ import annotations

from typing import Optional

from django.db.models import QuerySet

from apps.products.models import Product

class ProductSelector:
    @staticmethod
    def get_active_products() -> QuerySet[Product]:
        return Product.objects.filter(is_active=True, is_deleted=False)

    @staticmethod
    def get_by_id(product_id: str) -> Optional[Product]:
        try:
            return Product.objects.get(id=product_id, is_deleted=False)
        except Product.DoesNotExist:
            return None
```

## Views Pattern

Views should delegate to services/selectors, contain minimal logic.

```python
# apps/products/views/product_views.py
from __future__ import annotations

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.products.selectors.product_selector import ProductSelector
from apps.products.services.product_service import ProductService
from apps.products.serializers.product_serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return ProductSelector.get_active_products()

    @action(detail=True, methods=['post'])
    def update_price(self, request, pk=None):
        product = ProductSelector.get_by_id(pk)
        if not product:
            return Response({'error': 'Not found'}, status=404)
        new_price = request.data.get('price')
        updated = ProductService.update_price(product, new_price)
        return Response(ProductSerializer(updated).data)
```

## Serializers

```python
# apps/products/serializers/product_serializers.py
from __future__ import annotations

from rest_framework import serializers

from apps.products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
```

## URL Configuration

```python
# apps/products/urls.py
from __future__ import annotations

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.products.views.product_views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
]
```

```python
# backend/config/urls.py
from __future__ import annotations

from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('apps.products.urls')),
]
```

## Django REST Framework Settings

Key settings in `base.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.DefaultPageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

## pytest-django Usage

```python
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
```

```python
# tests/test_product.py
import pytest
from django.test import Client

from apps.products.models import Product

@pytest.fixture
def product(db):
    return Product.objects.create(name='Test', price='10.00')

def test_product_list(client, product):
    response = client.get('/api/v1/products/')
    assert response.status_code == 200
```

## Common Imports Pattern

```python
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

# Third party
from django.db import models
from rest_framework import serializers

# Django/DRF
from django.db.models import Q

# Local apps
from apps.common.models.base import UUIDModel, TimeStampedModel
from apps.accounts.models import User
```

## Migrations

- Use meaningful migration names: `python manage.py makemigrations products --name add_category`
- No manual changes to migration files
- Test migrations: `python manage.py migrate --check`

## Admin Configuration

```python
# apps/products/admin.py
from __future__ import annotations

from django.contrib import admin

from apps.products.models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
```