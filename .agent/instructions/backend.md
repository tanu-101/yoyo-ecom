<django_patterns>
<thin_views>
Views MUST NOT contain business logic.
- Logic -> Services.
- Queries -> Selectors.
Example: `product = ProductSelector.get_by_id(pk); ProductService.update(product, data)`.
</thin_views>

<services>
- Use static methods or functions.
- Handle exceptions and complex validation.
- Atomicity: Use `transaction.atomic` for multi-model writes.
- Keep services idempotent where external systems or retries may be involved.
- Do not query directly from views when a selector can express the read intent.
</services>

<selectors>
- Return Model instances or QuerySets.
- Centralize complex filters and related object prefetching (`select_related`, `prefetch_related`).
</selectors>

<migrations>
- Meaningful names: `python manage.py makemigrations <app> --name <description>`.
- Run migrations before PRs/Commits.
</migrations>

<implementation_order>
1. Models/migrations only when data shape changes.
2. Selectors for reads.
3. Services for writes/business rules.
4. Serializers/views/urls for API exposure.
5. Tests for services, selectors, permissions, and API behavior.
</implementation_order>
</django_patterns>
