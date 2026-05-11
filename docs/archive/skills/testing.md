# Testing Conventions

## Test Structure

Tests should be in `apps/<name>/tests/` directory:

```
apps/products/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_selectors.py
│   ├── test_services.py
│   └── test_views.py
```

## pytest Configuration

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
```

## Fixtures

### Using pytest-django fixtures

```python
import pytest
from django.test import Client

from apps.accounts.models import User
from apps.products.models import Product

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )

@pytest.fixture
def product(db):
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        price='99.99',
        sku='TEST-001'
    )
```

### Factory Pattern for Fixtures

```python
# apps/products/factories.py
import factory
from factory.django import DjangoModelFactory

from apps.products.models import Product

class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Product {n}')
    slug = factory.Sequence(lambda n: f'product-{n}')
    price = '99.99'
    sku = factory.Sequence(lambda n: f'SKU-{n:04d}')
    is_active = True
```

```python
# conftest.py
import pytest
from apps.products.factories import ProductFactory

@pytest.fixture
def product():
    return ProductFactory()
```

## Model Tests

```python
# apps/products/tests/test_models.py
import pytest

from apps.products.models import Product

@pytest.mark.django_db
class TestProductModel:
    def test_product_creation(self, product):
        assert product.name == 'Test Product'
        assert product.price == '99.99'
        assert product.is_active is True

    def test_product_str(self, product):
        assert str(product) == 'Test Product'

    def test_product_slug_generated(self, product):
        assert product.slug == 'test-product'

    def test_product_soft_delete(self, product):
        product.delete()
        product.refresh_from_db()
        assert product.is_deleted is True
```

## Service Tests

```python
# apps/products/tests/test_services.py
import pytest

from apps.products.services.product_service import ProductService
from apps.products.models import Product

@pytest.mark.django_db
class TestProductService:
    def test_create_product(self):
        product = ProductService.create_product(
            name='New Product',
            price='149.99'
        )
        assert product.id is not None
        assert product.name == 'New Product'

    def test_update_product_price(self, product):
        updated = ProductService.update_price(product, '199.99')
        assert updated.price == '199.99'
        product.refresh_from_db()
        assert product.price == '199.99'

    def test_activate_product(self, product):
        product.is_active = False
        product.save()
        activated = ProductService.activate(product)
        assert activated.is_active is True
```

## Selector Tests

```python
# apps/products/tests/test_selectors.py
import pytest

from apps.products.selectors.product_selector import ProductSelector

@pytest.mark.django_db
class TestProductSelector:
    def test_get_active_products(self, product):
        products = ProductSelector.get_active_products()
        assert products.count() >= 1

    def test_get_by_id(self, product):
        found = ProductSelector.get_by_id(str(product.id))
        assert found is not None
        assert found.id == product.id

    def test_get_by_id_not_found(self):
        found = ProductSelector.get_by_id('00000000-0000-0000-0000-000000000000')
        assert found is None

    def test_excludes_deleted(self, product):
        product.delete()
        products = ProductSelector.get_active_products()
        assert product not in products
```

## View Tests

```python
# apps/products/tests/test_views.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestProductViewSet:
    @pytest.fixture
    def api_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_list_products(self, api_client, product):
        url = reverse('products:product-list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert 'results' in response.data or isinstance(response.data, list)

    def test_create_product_authenticated(self, api_client):
        url = reverse('products:product-list')
        data = {
            'name': 'New Product',
            'price': '99.99',
            'sku': 'NEW-001'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 201

    def test_create_product_unauthenticated(self):
        client = APIClient()
        url = reverse('products:product-list')
        data = {'name': 'Test', 'price': '99.99'}
        response = client.post(url, data, format='json')
        assert response.status_code == 401

    def test_retrieve_product(self, api_client, product):
        url = reverse('products:product-detail', args=[product.id])
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['name'] == product.name

    def test_update_product(self, api_client, product):
        url = reverse('products:product-detail', args=[product.id])
        data = {'name': 'Updated Name', 'price': '149.99'}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == 200

    def test_delete_product(self, api_client, product):
        url = reverse('products:product-detail', args=[product.id])
        response = api_client.delete(url)
        assert response.status_code == 204
```

## API Test Helpers

```python
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client
```

## Admin Tests

```python
# apps/products/tests/test_admin.py
import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestProductAdmin:
    def test_admin_access(self, admin_client):
        url = reverse('admin:products_product_changelist')
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_customer_cannot_access_admin(self, authenticated_client):
        url = reverse('admin:products_product_changelist')
        response = authenticated_client.get(url)
        assert response.status_code == 403
```

## Testing Patterns

### Testing Permissions

```python
def test_only_admin_can_access(self, user, admin_user):
    # Customer access should fail
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/v1/admin/products/')
    assert response.status_code == 403

    # Admin access should succeed
    client.force_authenticate(user=admin_user)
    response = client.get('/api/v1/admin/products/')
    assert response.status_code == 200
```

### Testing Filters

```python
def test_filter_by_category(self, api_client, product):
    url = reverse('products:product-list')
    response = api_client.get(url, {'category': str(product.category.id)})
    assert response.status_code == 200
    assert len(response.data['results']) >= 1
```

### Testing Pagination

```python
def test_pagination(self, api_client):
    # Create multiple products
    for i in range(25):
        ProductFactory()

    url = reverse('products:product-list')
    response = api_client.get(url)
    assert 'count' in response.data
    assert 'next' in response.data
    assert 'previous' in response.data
```

## Coverage Configuration

```ini
# .coveragerc
[run]
source = apps
omit =
    */migrations/*
    */tests/*
    */factories.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific app tests
pytest apps/products/

# Run with coverage
pytest --cov=apps.products --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest apps/products/tests/test_models.py::TestProductModel::test_product_creation

# Run tests matching pattern
pytest -k "test_create"

# Stop on first failure
pytest -x
```

## Best Practices

1. **Use pytest-django** - `pytest.mark.django_db` for database access
2. **Test behavior, not implementation** - Test what the code does, not how
3. **Use descriptive test names** - `test_user_cannot_access_admin_panel`
4. **One assertion per test** - Makes failures easier to debug
5. **Use fixtures** - Reuse test data with pytest fixtures
6. **Test edge cases** - Empty lists, null values, boundaries
7. **Test permissions** - Ensure only authorized users can access
8. **Use factories** - Create test data consistently with factory_boy
9. **Clean up after tests** - Use transactions or rollback
10. **Run tests in CI** - Ensure all tests pass before merging