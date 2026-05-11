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
</services>

<selectors>
- Return Model instances or QuerySets.
- Centralize complex filters and related object prefetching (`select_related`, `prefetch_related`).
</selectors>

<migrations>
- Meaningful names: `python manage.py makemigrations <app> --name <description>`.
- Run migrations before PRs/Commits.
</migrations>
</django_patterns>
