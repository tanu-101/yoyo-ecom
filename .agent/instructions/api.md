<api_design>
<versioning>
Base path: `/api/v1/`
</versioning>

<namespaces>
Partitioned by audience:
- `public/`: No auth (Product list, Review list).
- `customer/`: JWT required (Cart, Order history, Profile).
- `admin/`: Staff only (Inventory management, Analytics).
- `webhooks/`: External services (Stripe callbacks).
</namespaces>

<status_codes>
- 200 OK: Successful GET/PATCH.
- 201 Created: Successful POST.
- 204 No Content: Successful DELETE.
- 400 Bad Request: Validation/Logic error.
- 401/403: Auth/Permission issues.
</status_codes>

<responses>
Consistent error format:
`{"error": "Main error message", "details": {"field": ["error details"]}}`
</responses>
</api_design>
