# Project README

# E-Commerce Management System


## Tech Stack

- **Backend**: Django 5, Django REST Framework
- **Language**: Python 3.11+
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: JWT (SimpleJWT)
- **Payments**: Stripe
- **Testing**: pytest, pytest-django
- **Code Quality**: Ruff, MyPy, Black

## Project Structure

```
backend/
├── config/           # Django settings
├── apps/            # Django apps (14 total)
│   ├── common/      # Shared utilities (base models, pagination)
│   ├── accounts/    # User authentication, roles
│   ├── catalog/     # Products, categories, variants
│   ├── inventory/   # Stock management
│   ├── carts/       # Shopping cart
│   ├── orders/      # Order management
│   ├── payments/    # Stripe integration
│   ├── shipping/    # Shipping methods
│   ├── returns/     # Return processing
│   ├── reviews/     # Product reviews
│   ├── wishlist/    # Wishlist
│   ├── coupons/     # Discount codes
│   ├── notifications/ # Email/SMS
│   └── analytics/   # Reporting
├── manage.py
└── pyproject.toml   # Dependencies and tool config
```

## Architecture Pattern

Each app follows the **service layer pattern**:
- `models/` - Database models only
- `selectors/` - Read/query logic
- `services/` - Business/write logic
- `views/` - Thin API layer

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, SQLite for dev)

### Installation

```bash
# Install dependencies
pip install -e .

# Run migrations
cd backend && python manage.py migrate

# Create superuser
cd backend && python manage.py createsuperuser

# Run development server
cd backend && python manage.py runserver
```

### Docker (Optional)

```bash
docker-compose up -d
```

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `DEBUG`
- `SECRET_KEY`
- `DATABASE_URL`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`

## API Endpoints

- `/api/v1/public/` - Public endpoints
- `/api/v1/customer/` - Customer endpoints (authenticated)
- `/api/v1/admin/` - Admin endpoints
- `/api/v1/webhooks/` - Stripe webhooks

## Tool Commands

```bash
# Run tests
cd backend && pytest

# Lint code
cd backend && ruff check .

# Format code
cd backend && ruff format .

# Type check
cd backend && mypy .

# Seed demo data
cd backend && python manage.py seed_data --customers 10 --staff 2 --admins 1
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## AI Agent Support

This project is optimized for AI coding agents (Gemini, Cursor, Claude Code, GitHub Copilot).

- `AGENTS.md` - Compact entry point for AI coding agents.
- `.agent/instructions/` - Modular source of truth for all agents.
- `GEMINI.md` - Entry point for Gemini CLI.
- `CLAUDE.md` - Entry point for Claude Code.
- `.cursorrules` - Root rules for Cursor IDE.
- `.cursor/rules/` - Modular, file-scoped rules for Cursor (.mdc files).
- `.github/copilot-instructions.md` - Context for GitHub Copilot.

## Documentation

- `docs/01-ARCHITECTURE.md` - System architecture
- `docs/api-v1-contract.md` - API specifications
- `docs/backend-plan.md` - Implementation roadmap
- `docs/auth-user-implementation-plan.md` - Next implementation plan
- `docs/database-final.md` - Database schema
- `.agent/instructions/` - Domain-specific guidance for agents

## License

[MIT](LICENSE)
