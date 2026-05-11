# GitHub Copilot Instructions

You are working on a Django REST API e-commerce management system.

## Project Context

- **Framework**: Django 5, Django REST Framework
- **Language**: Python 3.11+
- **Database**: PostgreSQL (prod), SQLite (dev)
- **Architecture**: Modular monolith with service layer

## Code Organization

Each Django app follows this pattern:
```
apps/<name>/
├── models/     → Database models only
├── selectors/   → Read/query logic
├── services/    → Business/write logic
├── views/       → Thin API layer (delegate to services)
├── serializers/ → DRF serializers
├── urls.py      → URL routing
└── admin.py     → Django admin
```

## Base Models

Always inherit from `apps/common/models/base.py`:
- `UUIDModel` - Provides UUID primary key
- `TimeStampedModel` - Adds created_at, updated_at
- `SoftDeleteModel` - Adds is_deleted, deleted_at (for soft delete)

## Coding Standards

### Imports (in order)
1. Standard library (`from __future__ import annotations`, `typing`)
2. Third party (`django`, `rest_framework`)
3. Django/DRF
4. Local apps (`from apps.common...`)

### Python Style
- Line length: 100
- Use `from __future__ import annotations`
- Use `TYPE_CHECKING` for type hints

### Django Patterns
- **Thin views, fat services** - Keep business logic in services
- **Use selectors for reads** - Query logic in selectors
- Use `rest_framework.viewsets.ModelViewSet`
- Use `django-filter` for filtering
- JWT authentication

## Important Rules

1. Use base models (UUIDModel, TimeStampedModel, SoftDeleteModel)
2. Follow app structure (models/, selectors/, services/, views/)
3. Never commit .env or secrets
4. Test with pytest
5. Lint with ruff

## API Structure

- `/api/v1/public/` - Public endpoints (catalog, reviews)
- `/api/v1/customer/` - Authenticated customer (cart, orders, wishlist)
- `/api/v1/admin/` - Admin endpoints (inventory, coupons, analytics)
- `/api/v1/webhooks/` - Stripe webhooks

## Example Code Pattern

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
```

## Commands

```bash
# Run server
cd backend && python manage.py runserver

# Run tests
cd backend && pytest

# Lint
cd backend && ruff check .

# Format
cd backend && ruff format .
```

## Read These Files First

- `AGENTS.md` - Main agent instructions
- `skills/django-backend.md` - Django patterns
- `skills/models.md` - Model conventions
- `skills/api-design.md` - API patterns
- `docs/api-v1-contract.md` - API specifications