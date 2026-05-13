<root>
<context>
Project: E-Commerce Management System (Django REST API)
Architecture: Modular Monolith with Service Layer
Stack: Django 5, DRF, Python 3.11+, PostgreSQL/SQLite
</context>

<base_models>
All models MUST inherit from these in `apps.common.models.base`:
- `UUIDModel`: `id` as UUID primary key.
- `TimeStampedModel`: `created_at` (fixed), `updated_at` (auto).
- `SoftDeleteModel`: `is_deleted` property, `deleted_at` field, `soft_delete()` method.
</base_models>

<app_structure>
Each app follows strict directory partitioning:
- `models/`: DB definitions only.
- `selectors/`: Read-only queries (get, filter, list).
- `services/`: Write operations & business logic (create, update, delete).
- `views/`: Thin API controllers (delegate to services/selectors).
- `serializers/`: Request validation & Response transformation.
</app_structure>

<standards>
- Line length: 100 characters.
- Strict Type Hints: Use `from __future__ import annotations` and explicit typing.
- Naming: CamelCase for classes, snake_case for functions/variables.
- Imports: Standard -> Third Party -> Django -> Local Apps.
</standards>

<engineering_principles>
- DRY: Reuse common models, exceptions, pagination, permissions, and response helpers.
- SOLID: Keep each module focused; services orchestrate workflows, selectors query data.
- KISS: Prefer explicit service functions/classes over generic frameworks.
- YAGNI: Do not add workers, event buses, microservices, or API v2 until required.
</engineering_principles>
</root>
