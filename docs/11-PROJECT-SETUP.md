# 🏭 Project Setup & Standards

## 📂 Backend Structure (Django)
The project follows a modular "Apps" structure where each business domain is isolated.

```text
apps/
├── authentication/ # JWT, Users, RBAC
├── products/       # Catalog, Categories, Search
├── inventory/      # Stock tracking, Concurrency logic
├── sales/          # Orders, Cart, Webhooks
├── returns/        # Return requests, Approvals
└── common/         # Shared mixins, utilities, base models

views/
├── api/            # REST ViewSets (DRF)
└── selectors/      # Pure functions for data retrieval

services/           # Business logic (Pure Python functions)
models/             # Database definitions
tests/              # pytest suite
```

---

## 🛠 Tech Stack & Tools
- **Language:** Python 3.12+
- **Framework:** Django 5.0 + Django REST Framework
- **Package Manager:** `uv` (Faster alternative to pip)
- **Linting/Formatting:** `ruff`
- **Type Checking:** `mypy`

---

## 🚀 Local Setup

### 1. Prerequisites
- Install Python 3.12
- Install `uv`: `pip install uv`
- PostgreSQL 15+ installed and running

### 2. Installation
```bash
# Clone the repository
git clone <repo-url>
cd ecommarce_management_system

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync
```

### 3. Environment Variables
Create a `.env` file in the root:
```env
DEBUG=True
SECRET_KEY=dev-secret-key
DATABASE_URL=postgres://user:pass@localhost:5432/ecommerce_db
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 4. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 📏 Coding Standards

### Service Layer Pattern
Logic should **never** live in `views.py` or `models.py`. Use pure Python functions in `services/`.
- **Bad:** `Order.objects.create(...)` in ViewSet.
- **Good:** `order_create_service(user=user, items=items)` in Service layer.

### ID Usage
- Use **UUID v4** for all public-facing IDs.
- Primary keys should always be UUIDs.

### Commits
Follow Conventional Commits:
- `feat: add stripe webhook integration`
- `fix: inventory leak on cancellation`
- `docs: update setup instructions`

---

## 🧪 Testing
We use `pytest` for all tests.
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps
```

---

**Related Documents:**
- [System Architecture](./01-ARCHITECTURE.md)
- [Security Requirements](./10-SECURITY.md)
