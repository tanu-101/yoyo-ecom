# Agent Instructions

Use this file as the compact entrypoint for AI coding agents.

## Source Of Truth

- Core rules: `.agent/instructions/core.md`
- Backend patterns: `.agent/instructions/backend.md`
- API rules: `.agent/instructions/api.md`
- Testing rules: `.agent/instructions/testing.md`
- Product/domain docs: `docs/backend-plan.md`, `docs/database-final.md`, `docs/api-v1-contract.md`

## Non-Negotiables

- Django apps live under `backend/apps/<domain>/`.
- API modules live under `backend/api/v1/<audience>/<domain>/`.
- Models define data and invariants only.
- Selectors own reads and query optimization.
- Services own writes, business rules, transactions, and integrations.
- Views/serializers stay thin: validate input, call selectors/services, return responses.
- Prefer explicit code over premature abstraction.
- Add or update tests with every behavior change.
- Use `factory_boy` factories in `apps/<domain>/factories.py` for reusable test data.

## Implementation Flow

1. Read the relevant existing app/module first.
2. Update models and migrations only when the domain data shape changes.
3. Add selectors for reads and services for writes.
4. Expose behavior through audience-specific API modules.
5. Cover happy path, edge cases, and permission/security cases with pytest.
6. Run `python backend/manage.py check`, `ruff`, `mypy`, and `pytest` when practical.

## Testing And Seed Data

- Service/business logic needs direct unit tests.
- Critical workflows need end-to-end API flow tests.
- Shared pytest fixtures live in `backend/conftest.py`.
- Seed/demo data belongs in idempotent Django management commands with count/prefix options.

## Current Priority

Start implementation with accounts/authentication and user APIs before deeper commerce flows.
