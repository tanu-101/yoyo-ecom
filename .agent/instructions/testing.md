<testing_rules>
<framework>
- Engine: `pytest` with `pytest-django`.
- Location: `apps/<name>/tests/`.
</framework>

<data_generation>
- Tool: `factory_boy`.
- Pattern: Create factories in `apps/<name>/factories.py`.
- Rule: Avoid manual `Model.objects.create()` in tests.
</data_generation>

<coverage>
- Goal: >80% coverage on new features.
- Command: `pytest --cov=apps`.
</coverage>

<scenarios>
- Test Happy Paths (200 OK).
- Test Edge Cases (empty input, null values).
- Test Security (invalid token, unauthorized role).
</scenarios>
</testing_rules>
