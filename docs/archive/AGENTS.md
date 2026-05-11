# AI Agent Instructions

This file provides context and rules for AI coding agents working on this e-commerce Django project.

## Project Overview

- **Type**: Django REST API e-commerce management system
- **Stack**: Django 5, Django REST Framework, Python 3.11+, PostgreSQL (SQLite for dev)
- **Pattern**: Modular monolith with service layer
- **Database**: PostgreSQL (prod), SQLite (local dev)

## Architecture

### App Structure (each app has)
```
apps/<name>/
├── models/
│   └── *.py          # Database models only (inherit from UUIDModel, TimeStampedModel, etc.)
├── selectors/
│   └── *.py          # Read/query logic
├── services/
│   └── *.py          # Business/write logic
├── views/
│   └── *.py          # Thin API layer (delegate to services/selectors)
├── serializers/
│   └── *.py          # DRF serializers
├── urls.py           # URL routing
└── admin.py          # Django admin
```

### Base Models (in apps/common/models/base.py)
- `UUIDModel` - Base with UUID primary key
- `TimeStampedModel` - Adds created_at, updated_at
- `SoftDeleteModel` - Adds is_deleted flag with deleted_at

### API Structure
- `/api/v1/public/` - Unauthenticated endpoints (catalog, products, reviews)
- `/api/v1/customer/` - Authenticated customer endpoints (cart, orders, wishlist)
- `/api/v1/admin/` - Admin/staff endpoints (inventory, coupons, analytics)
- `/api/v1/webhooks/` - Stripe webhooks

## Coding Standards

### Python
- Line length: 100
- Python 3.11+ syntax (use | for type unions, match/case allowed)
- Use `from __future__ import annotations` for forward references

### Django Patterns
- Thin views, fat services
- Use DRF ViewSets and ModelViewSets
- Custom pagination in `apps/common/pagination.py`
- JWT auth via `djangorestframework-simplejwt`
- Use `django-filter` for filtering

### Imports Order
1. Standard library
2. Third party
3. Django/DRF
4. Local apps (`from apps.common...`)

### File Organization
- Package-style modules (multiple small files, not large ones)
- Models in `models/` directory
- Services in `services/` directory
- Selectors in `selectors/` directory

## Current Implementation Status

- [x] Django project setup with 14 apps
- [x] Base models and common utilities
- [x] User authentication with roles (admin, staff, customer)
- [x] API URL routing scaffolded
- [x] Database configuration (SQLite dev, PostgreSQL prod)
- [ ] Full implementation of all apps (models, services, selectors, views)

## Key Files

| File | Purpose |
|------|---------|
| `backend/pyproject.toml` | Dependencies, tool configs (ruff, mypy, black, pytest) |
| `backend/config/settings/base.py` | Django settings |
| `backend/apps/common/models/base.py` | Base model classes |
| `backend/apps/common/pagination.py` | Custom pagination |
| `docs/api-v1-contract.md` | API endpoint specifications |
| `docs/backend-plan.md` | Implementation roadmap |
| `docs/database-final.md` | Database schema |
| `docker-compose.yml` | Local dev (Django + PostgreSQL) |

## Tool Commands

```bash
# Install dependencies
pip install -e .

# Run migrations
cd backend && python manage.py migrate

# Run development server
cd backend && python manage.py runserver

# Run tests
cd backend && pytest

# Lint code
cd backend && ruff check .

# Type check
cd backend && mypy .

# Format code
cd backend && ruff format .
```

## Environment Variables

See `backend/.env.example` for required environment variables:
- `DEBUG`, `SECRET_KEY`
- `DATABASE_URL` (PostgreSQL connection)
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`

## Important Rules for Agents

1. **Always read the relevant skill files** before making changes to a specific area
2. **Thin views, fat services** - Keep views minimal, business logic in services
3. **Use selectors for read operations** - Keep query logic in selectors
4. **Inherit from base models** - Use UUIDModel, TimeStampedModel, SoftDeleteModel
5. **Never commit secrets** - Don't commit .env or any file with real credentials
6. **Check existing patterns** - Follow the same patterns used in already-implemented apps
7. **Use pytest for testing** - Write tests in `apps/<name>/tests/`
8. **Run linting before committing** - Ensure ruff and mypy pass

## Skills Available

See `skills/` directory for domain-specific instructions:
- `skills/django-backend.md` - Django/DRF patterns
- `skills/models.md` - Model conventions
- `skills/api-design.md` - API design patterns
- `skills/testing.md` - Testing conventions
- `skills/security.md` - Security best practices

Read the relevant skill before working in that area.