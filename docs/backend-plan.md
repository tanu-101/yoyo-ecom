# Backend Build Plan

## Goal

Build the backend for a single-vendor e-commerce management system using Django, Django REST Framework, PostgreSQL, JWT authentication, Stripe payments, and a modular monolith architecture.

This plan intentionally starts with architecture, data modeling, and API contracts before implementation. The current project documentation is useful, but the database model and business boundaries need to be finalized before writing production code.

## Architecture Decision

Use a modular monolith.

Reasons:
- The system has tightly connected workflows: cart, inventory, order, payment, shipping, returns, and refunds.
- A single database keeps transactions simpler and safer.
- It avoids premature microservice complexity.
- The architecture can still evolve later because each domain is isolated in its own Django app.

Avoid in version 1:
- Microservices.
- Separate databases per module.
- API v2 before a breaking change exists.
- Background workers unless a feature truly requires async processing.

## Backend Folder Structure

```txt
backend/
├── manage.py
├── pyproject.toml
├── uv.lock
├── pytest.ini
├── ruff.toml
├── mypy.ini
├── .env.example
├── config/
│   ├── __init__.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── local.py
│       ├── production.py
│       └── test.py
├── apps/
│   ├── common/
│   ├── accounts/
│   ├── catalog/
│   ├── inventory/
│   ├── carts/
│   ├── orders/
│   ├── payments/
│   ├── shipping/
│   ├── returns/
│   ├── reviews/
│   ├── wishlist/
│   ├── coupons/
│   ├── notifications/
│   └── analytics/
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── urls.py
│       ├── public/
│       ├── customer/
│       ├── admin/
│       └── webhooks/
└── tests/
    ├── conftest.py
    ├── factories/
    ├── unit/
    ├── api/
    └── integration/
```

## Standard App Structure

Each domain app should use package-style modules instead of large single files. Avoid putting hundreds of lines into one `models.py`, `services.py`, or `selectors.py`.

```txt
apps/orders/
|-- __init__.py
|-- admin.py
|-- apps.py
|-- constants.py
|-- exceptions.py
|-- permissions.py
|-- signals.py
|-- tasks.py
|-- models/
|   |-- __init__.py
|   |-- order.py
|   |-- order_item.py
|   `-- status_history.py
|-- selectors/
|   |-- __init__.py
|   |-- orders.py
|   `-- order_items.py
|-- services/
|   |-- __init__.py
|   |-- checkout.py
|   |-- cancellation.py
|   `-- status_transitions.py
|-- migrations/
|   `-- __init__.py
`-- tests/
    |-- __init__.py
    |-- test_models.py
    |-- test_services.py
    `-- test_selectors.py
```

Responsibilities:
- `models/`: database structure and model-level invariants only.
- `selectors/`: read/query logic.
- `services/`: business/write logic.
- `permissions.py`: app-specific authorization.
- `exceptions.py`: domain-specific errors.
- `constants.py`: enums, choices, status values.
- `signals.py`: only for unavoidable framework integration, not primary business workflows.
- `tasks.py`: async jobs if introduced later.

For small apps, it is acceptable to start with one file inside each package, such as `models/notification.py` or `services/preferences.py`. Do not collapse back to a root-level `models.py` or `services.py`.

## Recommended Module Splits

```txt
apps/accounts/
|-- models/user.py
|-- models/staff_permission.py
|-- models/address.py
|-- services/authentication.py
|-- services/staff_permissions.py
`-- selectors/users.py

apps/catalog/
|-- models/category.py
|-- models/product.py
|-- models/product_image.py
|-- models/variant.py
|-- models/variant_attribute.py
|-- services/products.py
|-- services/variants.py
`-- selectors/products.py

apps/inventory/
|-- models/inventory_transaction.py
|-- models/stock_reservation.py
|-- services/stock_adjustments.py
|-- services/stock_locks.py
`-- selectors/stock.py

apps/payments/
|-- models/payment.py
|-- models/payment_event.py
|-- models/refund.py
|-- services/stripe_payment_intents.py
|-- services/stripe_webhooks.py
|-- services/refunds.py
`-- selectors/payments.py

apps/returns/
|-- models/return_request.py
|-- models/return_item.py
|-- models/return_image.py
|-- models/status_history.py
|-- services/eligibility.py
|-- services/approval.py
|-- services/processing.py
`-- selectors/returns.py
```

## Domain Boundaries

### common

Shared backend primitives:
- UUID base model.
- timestamp fields.
- soft delete base model, if needed.
- common exceptions.
- API response helpers.
- pagination.
- permission base classes.
- audit mixins.

Keep `common` small. Do not place business rules here.

### accounts

Owns:
- custom user model.
- roles.
- staff permissions.
- customer profile.
- saved addresses.
- authentication support.

Does not own:
- JWT endpoint implementation details in API serializers/views.
- order ownership rules outside permission helpers.

### catalog

Owns:
- products.
- categories.
- variants.
- product images.
- variant attributes.
- public product listing and product state.

Does not own:
- stock mutation.
- checkout rules.

### inventory

Owns:
- stock quantities.
- inventory transactions.
- safe stock increase/decrease.
- stock reservation, if used.
- low-stock alerts later.

All stock mutations should go through inventory services.

### carts

Owns:
- active customer cart.
- cart items.
- cart calculations.
- coupon attachment to cart.

Does not own:
- final order creation.
- permanent payment totals.

### orders

Owns:
- order records.
- order items.
- checkout orchestration.
- order status transitions.
- cancellation.
- status history.

Checkout should call inventory, coupons, shipping, and payments through services.

### payments

Owns:
- payment records.
- Stripe payment intent creation.
- Stripe webhook verification.
- payment events for idempotency.
- refunds.

Does not own:
- order lifecycle except through explicit order service calls.

### shipping

Owns:
- shipping methods.
- shipping cost calculation.
- order shipping address snapshot.
- tracking data.

### returns

Owns:
- return requests.
- return items.
- return status flow.
- admin decisions.
- resolution choice: refund, replacement, store credit.

### reviews

Owns:
- product reviews.
- review images.
- review eligibility.
- moderation state.

### wishlist

Owns:
- wishlist items.
- move-to-cart workflow.

### coupons

Owns:
- coupon definitions.
- coupon validation.
- per-customer redemption limits.
- usage counters.

### notifications

Owns:
- notification preferences.
- email/SMS logs.
- notification sending adapters.

### analytics

Owns:
- read-only reporting queries.
- dashboard metrics.

Prefer selectors over stored analytics tables in version 1 unless performance requires snapshots later.

## API Versioning

Use path versioning:

```txt
/api/v1/
```

Initial version:

```txt
api/v1/
```

Create `api/v2/` only when a breaking API change is needed.

## API Surface Separation

Separate API modules by audience and permission scope. Domain apps own business logic; API modules only expose that logic with the correct serializers, filters, and permissions.

```txt
api/v1/
|-- public/
|   |-- catalog/
|   |-- reviews/
|   `-- shipping/
|-- customer/
|   |-- auth/
|   |-- profile/
|   |-- addresses/
|   |-- cart/
|   |-- orders/
|   |-- payments/
|   |-- returns/
|   |-- reviews/
|   |-- wishlist/
|   `-- notifications/
|-- admin/
|   |-- users/
|   |-- staff/
|   |-- catalog/
|   |-- inventory/
|   |-- orders/
|   |-- payments/
|   |-- shipping/
|   |-- returns/
|   |-- reviews/
|   |-- coupons/
|   |-- notifications/
|   `-- analytics/
`-- webhooks/
    `-- stripe/
```

Route groups:

```txt
/api/v1/public/
/api/v1/customer/
/api/v1/admin/
/api/v1/webhooks/
```

Permission rules:
- Public APIs must explicitly allow anonymous access.
- Customer APIs require authentication and customer ownership checks.
- Admin APIs require admin access or staff access with explicit permission codes.
- Webhook APIs use provider verification, not user authentication.

This avoids mixing customer and admin behavior in the same view files.

## Implementation Sequence

### Step 1: Scaffold Backend

- Create Django project under `backend/`.
- Configure `config/settings/base.py`, `local.py`, `production.py`, and `test.py`.
- Install core dependencies:
  - Django.
  - Django REST Framework.
  - djangorestframework-simplejwt.
  - django-cors-headers.
  - psycopg.
  - django-filter.
  - drf-spectacular.
  - pytest, pytest-django, pytest-cov.
  - ruff, mypy.

### Step 2: Build common

- UUID base model.
- timestamp model.
- optional soft delete model.
- common pagination.
- common exceptions.
- API error format.
- audit fields where needed.

### Step 3: Build accounts

- Custom user model.
- Role and permission structure.
- JWT auth.
- registration/login/logout/me endpoints.
- admin/staff/customer permission helpers.

### Step 4: Build catalog

- Category.
- Product.
- ProductImage.
- Variant.
- VariantAttribute.
- VariantAttributeValue.
- public product list/detail.
- admin product management.

### Step 5: Build inventory

- InventoryTransaction.
- stock adjustment services.
- safe stock decrement with `select_for_update`.
- stock restoration service.

### Step 6: Build carts

- Cart.
- CartItem.
- add/update/remove item.
- cart totals.
- coupon application placeholder or full coupon integration if coupons are ready.

### Step 7: Build orders

- Order.
- OrderItem.
- OrderStatusHistory.
- checkout service.
- cancellation service.
- customer/admin order views.

### Step 8: Build payments

- Payment.
- PaymentEvent.
- Refund.
- Stripe payment intent.
- Stripe webhook.
- webhook idempotency.
- payment-to-order transition.

### Step 9: Build shipping

- ShippingMethod.
- shipping address snapshot.
- order tracking.
- admin tracking update.

### Step 10: Build returns

- ReturnRequest.
- ReturnItem.
- ReturnStatusHistory.
- request validation.
- approve/reject.
- process refund/replacement/store credit.

### Step 11: Build supporting modules

- coupons.
- reviews.
- wishlist.
- notifications.
- analytics.

### Step 12: Hardening

- rate limiting.
- security headers.
- CORS.
- CSRF policy.
- audit logging.
- structured logging.
- OpenAPI schema.
- full test pass.

## Business Rules To Finalize Before Coding

Use these version 1 decisions unless changed deliberately:

- User roles: `admin`, `staff`, and `customer`.
- Staff access: disabled by default and enabled through explicit permission codes.
- JWT storage: access and refresh tokens returned in the response body; clients send access token with the `Authorization: Bearer <token>` header.
- Product deletion: soft delete/archive for catalog objects.
- Product images: store URL/path strings first; add S3 or another object storage adapter later.
- Variant attributes: normalized `VariantAttribute`, `VariantAttributeValue`, and `VariantOption`.
- Inventory policy: deduct stock at checkout/order creation; restore stock if payment expires, order is cancelled, or return is received and accepted.
- Cart expiration: no automatic expiration in the first implementation.
- Unpaid order expiration: 24 hours.
- Paid order cancellation: customers can request cancellation before shipped; admin can cancel before delivered and trigger refund workflow if paid.
- Return stock restoration: restore after warehouse receipt and acceptance, not immediately on return approval.
- Return request items: support multiple return items per request.
- Coupon stacking: one coupon per cart/order in version 1.
- Shipping cost: use `base_price + (price_per_kg * total_weight)` when weight exists; otherwise use base price.
- Notifications: email first; SMS adapter can be added behind the notifications service.

## Engineering Principles

### DRY

Avoid repeating infrastructure code. Reuse base models, permissions, pagination, and API error formatting. Do not abstract domain services too early.

### SOLID

Keep views thin. Put business workflows in services. Put read logic in selectors. Keep each app focused on one business area.

### YAGNI

Do not add microservices, workers, event buses, API v2, complex warehouse automation, or advanced analytics snapshots until there is a real need.

### KISS

Prefer explicit service functions and clear transaction boundaries over deep inheritance or generic frameworks.

## Definition Of Done For Backend V1

- All core models migrated.
- API v1 documented with OpenAPI.
- Authentication and RBAC enforced server-side.
- Checkout is transactional and prevents overselling.
- Stripe webhook is verified and idempotent.
- Customers can only access their own data.
- Admin/staff permissions are tested.
- Cancellation restores stock when valid.
- Returns follow the documented workflow.
- Critical workflows have integration tests.
- Ruff, mypy, and pytest pass.
