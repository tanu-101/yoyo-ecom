<testing_rules>
<framework>
- Engine: `pytest` with `pytest-django`.
- Location: `apps/<name>/tests/`.
</framework>

<data_generation>
- Tool: `factory_boy`.
- Pattern: Create factories in `apps/<name>/factories.py`.
- Rule: Avoid manual `Model.objects.create()` in tests when a factory exists.
- Shared fixtures belong in `backend/conftest.py`; app-specific helpers belong in `apps/<name>/tests/`.
</data_generation>

<coverage>
- Goal: >80% coverage on new features.
- Command: `pytest --cov=apps`.
</coverage>

<scenarios>
- Unit-test services for business rules, transactions, and validation.
- Test selectors for filtering, ownership, and visibility rules.
- API tests must cover happy paths, validation errors, and unauthorized/forbidden access.
- Add end-to-end flow tests for critical user/business journeys.
</scenarios>

<seed_data>
- Seed/demo data should use Django management commands named `seed_<domain>` or `seed_data`.
- Seed commands must be idempotent and accept count/prefix options.
- Test seed commands with pytest by calling `django.core.management.call_command`.
</seed_data>
</testing_rules>
