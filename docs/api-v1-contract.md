# API V1 Contract

## Base URL

```txt
/api/v1/
```

## Route Groups

```txt
/api/v1/public/
/api/v1/customer/
/api/v1/admin/
/api/v1/webhooks/
```

Use separate API modules by audience:
- `public`: anonymous browsing APIs.
- `customer`: authenticated customer self-service APIs.
- `admin`: admin panel and staff-permission APIs.
- `webhooks`: provider callbacks such as Stripe.

## Response Format

Success response:

```json
{
  "data": {},
  "message": "Success"
}
```

List response:

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

Error response:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid request.",
    "fields": {}
  }
}
```

## Common Status Codes

```txt
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
429 Too Many Requests
500 Internal Server Error
```

## Auth

### POST /customer/auth/register/

Create a customer account.

Auth: public.

Request:

```json
{
  "email": "customer@example.com",
  "password": "StrongPass123!",
  "first_name": "Jane",
  "last_name": "Doe",
  "phone": "+8801000000000"
}
```

Response:

```json
{
  "data": {
    "id": "uuid",
    "email": "customer@example.com",
    "role": "customer"
  }
}
```

Errors:
- duplicate email.
- weak password.
- invalid email.

### POST /customer/auth/login/

Auth: public.

Request:

```json
{
  "email": "customer@example.com",
  "password": "StrongPass123!"
}
```

Response:

```json
{
  "data": {
    "access": "jwt-access-token",
    "refresh": "jwt-refresh-token",
    "user": {
      "id": "uuid",
      "email": "customer@example.com",
      "role": "customer"
    }
  }
}
```

### POST /customer/auth/refresh/

Auth: public.

Request:

```json
{
  "refresh": "jwt-refresh-token"
}
```

### POST /customer/auth/logout/

Auth: authenticated.

Request:

```json
{
  "refresh": "jwt-refresh-token"
}
```

### GET /customer/auth/me/

Auth: authenticated.

Response:

```json
{
  "data": {
    "id": "uuid",
    "email": "customer@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "role": "customer",
    "permissions": []
  }
}
```

## Users And Staff

### GET /admin/users/

List users.

Auth: admin.

Query:

```txt
role=customer|staff|admin
search=email_or_name
is_active=true|false
page=1
page_size=20
```

### GET /admin/users/{id}/

Auth:
- admin can view any user.
- customer can view self.

### PATCH /admin/users/{id}/

Auth:
- admin can update allowed user fields.
- customer can update own profile fields.

### POST /admin/staff/

Create staff account.

Auth: admin.

Request:

```json
{
  "email": "staff@example.com",
  "first_name": "Staff",
  "last_name": "User",
  "permissions": ["orders.view", "orders.update_status"]
}
```

### PATCH /admin/staff/{id}/permissions/

Auth: admin.

Request:

```json
{
  "permissions": [
    {"code": "orders.view", "is_enabled": true},
    {"code": "products.create", "is_enabled": false}
  ]
}
```

## Addresses

### GET /customer/addresses/

Auth: customer.

Returns current user's saved addresses.

### POST /customer/addresses/

Auth: customer.

Request:

```json
{
  "full_name": "Jane Doe",
  "phone": "+8801000000000",
  "line1": "House 1, Road 2",
  "line2": "Apt 3",
  "city": "Dhaka",
  "state": "Dhaka",
  "postal_code": "1207",
  "country": "Bangladesh",
  "is_default": true
}
```

### PATCH /customer/addresses/{id}/

Auth: owner.

### DELETE /customer/addresses/{id}/

Auth: owner.

Soft delete.

## Catalog

### GET /public/catalog/categories/

Auth: public.

Returns active categories.

### POST /admin/catalog/categories/

Auth: admin.

Staff: requires `products.create`.

### PATCH /admin/catalog/categories/{id}/

Auth: admin.

Staff: requires `products.update`.

### DELETE /admin/catalog/categories/{id}/

Auth: admin.

Soft delete.

### GET /public/catalog/products/

Auth: public.

Query:

```txt
search=
category=
min_price=
max_price=
in_stock=true|false
sort=newest|price_asc|price_desc|popular|rating
page=1
page_size=20
```

Response includes:
- product summary.
- primary image.
- active variants summary.
- calculated stock availability.

### POST /admin/catalog/products/

Auth: admin.

Staff: requires `products.create`.

Request:

```json
{
  "category": "uuid",
  "name": "T-Shirt",
  "description": "Cotton t-shirt",
  "base_price": "20.00",
  "status": "active",
  "images": [
    {"image": "url-or-upload-reference", "alt_text": "Front", "is_primary": true}
  ]
}
```

### GET /public/catalog/products/{id}/

Auth: public.

### PATCH /admin/catalog/products/{id}/

Auth: admin.

Staff: requires `products.update`.

### DELETE /admin/catalog/products/{id}/

Auth: admin.

Soft delete or archive.

### POST /admin/catalog/products/{id}/variants/

Auth: admin.

Staff: requires `products.create`.

Request:

```json
{
  "sku": "TSHIRT-RED-M",
  "name": "Red - M",
  "price": "20.00",
  "stock_quantity": 10,
  "status": "active",
  "options": [
    {"attribute": "Color", "value": "Red"},
    {"attribute": "Size", "value": "M"}
  ]
}
```

### PATCH /admin/catalog/variants/{id}/

Auth: admin.

Staff: requires `products.update`.

Note:
- Direct stock update should not be done here after inventory module exists.
- Use inventory adjustment endpoint for stock changes.

## Inventory

### GET /admin/inventory/variants/

Auth: admin.

Staff: requires `inventory.view`.

Query:

```txt
search=
low_stock=true|false
page=1
page_size=20
```

### POST /admin/inventory/adjustments/

Auth: admin.

Request:

```json
{
  "variant": "uuid",
  "quantity_changed": 5,
  "notes": "Restock"
}
```

Rules:
- Positive quantity increases stock.
- Negative quantity decreases stock.
- Resulting stock cannot be below zero.
- Creates `InventoryTransaction`.

### GET /admin/inventory/transactions/

Auth: admin.

Staff: requires `inventory.view`.

## Cart

### GET /customer/cart/

Auth: customer.

### POST /customer/cart/items/

Auth: customer.

Request:

```json
{
  "variant": "uuid",
  "quantity": 2
}
```

Errors:
- product inactive.
- variant inactive.
- insufficient stock.

### PATCH /customer/cart/items/{id}/

Auth: owner.

Request:

```json
{
  "quantity": 3
}
```

### DELETE /customer/cart/items/{id}/

Auth: owner.

### POST /customer/cart/apply-coupon/

Auth: customer.

Request:

```json
{
  "code": "SUMMER10"
}
```

### DELETE /customer/cart/coupon/

Auth: customer.

## Orders

### POST /customer/orders/checkout/

Create an order from the current cart.

Auth: customer.

Request:

```json
{
  "address_id": "uuid",
  "shipping_method": "uuid",
  "customer_notes": "Leave at reception"
}
```

Response:

```json
{
  "data": {
    "id": "uuid",
    "order_number": "ORD-2026-000001",
    "status": "pending_payment",
    "payment_status": "pending",
    "total_amount": "100.00"
  }
}
```

Rules:
- Cart cannot be empty.
- Re-check all prices and stock.
- Use transaction.
- Lock variant rows.
- Deduct or reserve stock based on final stock policy.
- Snapshot product, variant, price, and address.

### GET /customer/orders/

Auth: customer.

Returns the authenticated customer's own orders.

Query:

```txt
status=
payment_status=
customer=
date_from=
date_to=
page=1
page_size=20
```

### GET /customer/orders/{id}/

Auth: owner.

Returns one order owned by the authenticated customer.

### GET /admin/orders/

Auth:
- admin.
- staff requires `orders.view`.

Returns all orders for the admin panel.

### GET /admin/orders/{id}/

Auth:
- admin.
- staff requires `orders.view`.

### POST /customer/orders/{id}/cancel/

Auth:
- customer can cancel own order before shipped.
- admin can cancel according to policy.

Request:

```json
{
  "reason": "Changed my mind"
}
```

Rules:
- Restore stock when cancellation succeeds.
- Update status history.
- Refund if already paid and policy allows.

### POST /admin/orders/{id}/status/

Auth:
- admin.
- staff requires `orders.update_status`.

Request:

```json
{
  "status": "processing",
  "reason": "Packed"
}
```

Allowed transitions:

```txt
pending_payment -> placed
placed -> processing
processing -> shipped
shipped -> delivered
placed -> cancelled
processing -> cancelled
```

## Payments

### POST /customer/payments/create-intent/

Auth: customer.

Request:

```json
{
  "order": "uuid"
}
```

Response:

```json
{
  "data": {
    "client_secret": "stripe-client-secret",
    "payment": "uuid"
  }
}
```

Rules:
- Order must belong to customer.
- Order must be `pending_payment`.
- Amount must match order total.

### POST /webhooks/stripe/

Auth: Stripe signature.

Rules:
- Verify Stripe signature.
- Store event in `PaymentEvent`.
- Ignore duplicate event IDs.
- On payment success, mark payment succeeded and order placed/paid.
- On payment failure, mark payment failed.

### GET /customer/payments/

Auth: customer.

Returns the authenticated customer's own payments.

### GET /admin/payments/

Auth: admin.

### POST /admin/payments/{id}/refund/

Auth: admin.

Request:

```json
{
  "amount": "50.00",
  "reason": "Approved return"
}
```

## Shipping

### GET /public/shipping/methods/

Auth: public.

Returns active shipping methods.

### POST /admin/orders/{id}/tracking/

Auth:
- admin.
- staff requires `orders.update_status`.

Request:

```json
{
  "carrier": "FedEx",
  "tracking_number": "TRACK123",
  "tracking_url": "https://carrier.example/track/TRACK123",
  "estimated_delivery": "2026-05-20"
}
```

### PATCH /admin/orders/{id}/tracking/

Auth:
- admin.
- staff requires `orders.update_status`.

## Returns

### POST /customer/returns/

Create a return request.

Auth: customer.

Request:

```json
{
  "order": "uuid",
  "reason": "damaged",
  "comments": "Item arrived damaged.",
  "resolution": "refund",
  "items": [
    {
      "order_item": "uuid",
      "quantity": 1,
      "reason": "damaged"
    }
  ],
  "images": ["url-or-upload-reference"]
}
```

Rules:
- Order must belong to customer.
- Order must be delivered.
- Must be inside return window.
- Quantity cannot exceed purchased quantity minus already returned quantity.

### GET /customer/returns/

Auth: customer.

Returns the authenticated customer's own return requests.

### GET /customer/returns/{id}/

Auth: owner.

### GET /admin/returns/

Auth:
- admin.
- staff requires `returns.view`.

### GET /admin/returns/{id}/

Auth:
- admin.
- staff requires `returns.view`.

### POST /admin/returns/{id}/approve/

Auth: admin.

Request:

```json
{
  "resolution": "refund",
  "admin_notes": "Approved after review.",
  "refund_amount": "50.00"
}
```

### POST /admin/returns/{id}/reject/

Auth: admin.

Request:

```json
{
  "rejection_reason": "Outside return window"
}
```

### POST /admin/returns/{id}/mark-received/

Auth: admin.

### POST /admin/returns/{id}/process/

Auth: admin.

Rules:
- For refund, create refund record.
- For replacement, create replacement order.
- For store credit, create credit record if store credit is included in version 1.

## Reviews

### GET /public/reviews/products/{id}/

Auth: public.

Shows approved reviews.

### POST /customer/reviews/

Auth: customer.

Request:

```json
{
  "order_item": "uuid",
  "rating": 5,
  "title": "Great product",
  "content": "Good quality.",
  "images": []
}
```

Rules:
- Customer must own order item.
- Order must be delivered.
- One review per order item.

### PATCH /customer/reviews/{id}/

Auth: review owner.

### POST /admin/reviews/{id}/approve/

Auth: admin.

### POST /admin/reviews/{id}/reject/

Auth: admin.

## Wishlist

### GET /customer/wishlist/

Auth: customer.

### POST /customer/wishlist/

Auth: customer.

Request:

```json
{
  "product": "uuid",
  "variant": "uuid",
  "notes": "Buy later"
}
```

### DELETE /customer/wishlist/{id}/

Auth: owner.

### POST /customer/wishlist/{id}/move-to-cart/

Auth: owner.

Request:

```json
{
  "quantity": 1
}
```

## Coupons

### GET /admin/coupons/

Auth: admin.

### POST /admin/coupons/

Auth: admin.

Request:

```json
{
  "code": "SUMMER10",
  "discount_type": "percentage",
  "discount_value": "10.00",
  "min_order_value": "50.00",
  "max_discount_amount": "20.00",
  "max_usage_count": 100,
  "per_customer_limit": 1,
  "valid_from": "2026-05-01T00:00:00Z",
  "valid_until": "2026-06-01T00:00:00Z",
  "is_active": true
}
```

### PATCH /admin/coupons/{id}/

Auth: admin.

### DELETE /admin/coupons/{id}/

Auth: admin.

Soft delete or deactivate.

## Notifications

### GET /customer/notifications/preferences/

Auth: authenticated.

### PATCH /customer/notifications/preferences/

Auth: authenticated.

Request:

```json
{
  "order_updates_email": true,
  "order_updates_sms": false,
  "promotions_email": false,
  "promotions_sms": false
}
```

### GET /customer/notifications/

Auth: authenticated.

Returns user's in-app notifications.

## Analytics

### GET /admin/analytics/summary/

Auth: admin.

Response:

```json
{
  "data": {
    "total_orders": 100,
    "total_revenue": "10000.00",
    "average_order_value": "100.00",
    "return_rate": "2.50"
  }
}
```

### GET /admin/analytics/sales/

Auth: admin.

Query:

```txt
date_from=
date_to=
group_by=day|week|month
```

### GET /admin/analytics/products/top/

Auth: admin.

### GET /admin/analytics/returns/

Auth: admin.

## Permission Summary

```txt
Public:
- register/login
- product list/detail
- category list
- product reviews
- shipping methods

Customer:
- own profile
- own addresses
- own cart
- own orders
- own payments
- own returns
- own wishlist
- own reviews
- own notification preferences

Staff:
- configurable permissions only

Admin:
- full system access
```

## Critical Error Codes

```txt
auth_invalid_credentials
auth_token_expired
permission_denied
validation_error
not_found
duplicate_resource
insufficient_stock
cart_empty
invalid_order_status_transition
payment_already_processed
stripe_signature_invalid
return_window_expired
return_not_eligible
coupon_invalid
coupon_expired
coupon_usage_limit_reached
review_not_eligible
rate_limited
```
