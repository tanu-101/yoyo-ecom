# Final Backend Database Design

## Purpose

This document finalizes the backend data model before implementation. It extends the current schema with missing production concerns:

- auditability.
- API-safe UUID identifiers.
- order and return status history.
- payment webhook idempotency.
- inventory transaction logs.
- coupon redemption tracking.
- order address snapshots.
- normalized product images and variant attributes.

## Global Model Standards

Use these fields on most business models:

```txt
id UUID primary key
created_at datetime
updated_at datetime
```

Use soft delete only where deletion would break history:

```txt
deleted_at datetime nullable
```

Recommended soft-delete models:
- User.
- Product.
- Category.
- Variant.
- Coupon.

Avoid soft delete on immutable history rows:
- OrderItem.
- PaymentEvent.
- InventoryTransaction.
- OrderStatusHistory.
- ReturnStatusHistory.

## accounts

### User

```txt
id UUID PK
email string unique
username string unique nullable
password string
first_name string
last_name string
phone string nullable
profile_picture string nullable
role string enum(admin, staff, customer)
is_active boolean
is_staff boolean
is_superuser boolean
is_email_verified boolean
last_login datetime nullable
date_joined datetime
deleted_at datetime nullable
created_at datetime
updated_at datetime
```

Indexes:
- unique email.
- unique username.
- role.
- is_active.

Notes:
- Use Django's custom user model.
- Keep role simple in version 1.
- Use a separate `StaffPermission` model for configurable staff access.

### StaffPermission

```txt
id UUID PK
user FK User
permission_code string
is_enabled boolean
granted_by FK User nullable
granted_at datetime nullable
created_at datetime
updated_at datetime
```

Constraints:
- unique `(user, permission_code)`.
- `user.role` must be `staff`.

Initial permission codes:

```txt
products.view
products.create
products.update
orders.view
orders.update_status
returns.view
support.view_customers
inventory.view
```

### Address

Saved customer address.

```txt
id UUID PK
user FK User
full_name string
phone string
line1 string
line2 string nullable
city string
state string nullable
postal_code string
country string
is_default boolean
created_at datetime
updated_at datetime
deleted_at datetime nullable
```

Indexes:
- user.
- `(user, is_default)`.

## catalog

### Category

```txt
id UUID PK
name string
slug string unique
description text nullable
parent FK Category nullable
image string nullable
is_active boolean
sort_order integer
created_at datetime
updated_at datetime
deleted_at datetime nullable
```

Indexes:
- slug.
- parent.
- is_active.

### Product

```txt
id UUID PK
category FK Category
name string
slug string unique
description text
base_price decimal(10, 2)
status enum(draft, active, inactive, archived)
is_featured boolean
created_by FK User nullable
created_at datetime
updated_at datetime
deleted_at datetime nullable
```

Indexes:
- slug.
- category.
- status.
- `(category, status)`.

Notes:
- Public catalog should show only `status=active`.
- Product stock is calculated from variants, not stored here.

### ProductImage

```txt
id UUID PK
product FK Product
image string
alt_text string nullable
sort_order integer
is_primary boolean
created_at datetime
updated_at datetime
```

Indexes:
- product.
- `(product, is_primary)`.

### VariantAttribute

Examples: Color, Size, Material.

```txt
id UUID PK
name string unique
slug string unique
created_at datetime
updated_at datetime
```

### VariantAttributeValue

Examples: Red, Blue, Small, Medium.

```txt
id UUID PK
attribute FK VariantAttribute
value string
slug string
created_at datetime
updated_at datetime
```

Constraints:
- unique `(attribute, value)`.
- unique `(attribute, slug)`.

### Variant

```txt
id UUID PK
product FK Product
sku string unique
name string
price decimal(10, 2)
stock_quantity integer
status enum(active, inactive)
image string nullable
created_at datetime
updated_at datetime
deleted_at datetime nullable
```

Indexes:
- product.
- sku.
- status.
- `(product, status)`.
- `(product, stock_quantity)`.

Rules:
- `stock_quantity >= 0`.
- Stock changes only through inventory services.

### VariantOption

Connects a variant to its attributes.

```txt
id UUID PK
variant FK Variant
attribute FK VariantAttribute
value FK VariantAttributeValue
created_at datetime
updated_at datetime
```

Constraints:
- unique `(variant, attribute)`.

## inventory

### InventoryTransaction

Immutable stock audit log.

```txt
id UUID PK
variant FK Variant
transaction_type enum(order_placed, cancellation, return_received, refund, manual_adjustment, correction)
quantity_changed integer
stock_before integer
stock_after integer
reference_type string nullable
reference_id UUID nullable
notes text nullable
created_by FK User nullable
created_at datetime
```

Indexes:
- variant.
- transaction_type.
- created_at.
- `(reference_type, reference_id)`.

Rules:
- `quantity_changed` can be positive or negative.
- `stock_after` must equal `stock_before + quantity_changed`.

### StockReservation

Optional but recommended if orders are created before payment.

```txt
id UUID PK
variant FK Variant
user FK User
order FK Order nullable
quantity integer
status enum(active, consumed, released, expired)
expires_at datetime
created_at datetime
updated_at datetime
```

Indexes:
- variant.
- user.
- order.
- status.
- expires_at.

Version 1 decision needed:
- Either deduct stock at checkout immediately.
- Or reserve stock until payment succeeds.

For simpler version 1, deduct stock when order is created and restore stock if payment expires or order is cancelled.

## carts

### Cart

```txt
id UUID PK
customer FK User unique
coupon FK Coupon nullable
created_at datetime
updated_at datetime
```

Indexes:
- unique customer.
- updated_at.

Notes:
- Cart totals can be calculated dynamically.
- Avoid storing derived totals unless performance requires it.

### CartItem

```txt
id UUID PK
cart FK Cart
product FK Product
variant FK Variant
quantity integer
unit_price decimal(10, 2)
created_at datetime
updated_at datetime
```

Constraints:
- unique `(cart, variant)`.
- `quantity > 0`.

Indexes:
- cart.
- variant.

Notes:
- `unit_price` can be refreshed from variant price while still in cart.
- Final order price must be snapshotted in `OrderItem`.

## coupons

### Coupon

```txt
id UUID PK
code string unique
description text nullable
discount_type enum(percentage, fixed_amount)
discount_value decimal(10, 2)
min_order_value decimal(10, 2)
max_discount_amount decimal(10, 2) nullable
max_usage_count integer nullable
usage_count integer
per_customer_limit integer
valid_from datetime
valid_until datetime nullable
is_active boolean
created_at datetime
updated_at datetime
deleted_at datetime nullable
```

Indexes:
- code.
- is_active.
- valid_from.
- valid_until.

### CouponRedemption

```txt
id UUID PK
coupon FK Coupon
customer FK User
order FK Order
discount_amount decimal(10, 2)
created_at datetime
```

Constraints:
- unique `(coupon, order)`.

Indexes:
- coupon.
- customer.
- `(coupon, customer)`.

## orders

### Order

```txt
id UUID PK
order_number string unique
customer FK User
status enum(pending_payment, placed, processing, shipped, delivered, cancelled)
payment_status enum(pending, paid, failed, partially_refunded, refunded)
coupon FK Coupon nullable
subtotal decimal(10, 2)
discount_amount decimal(10, 2)
shipping_cost decimal(10, 2)
tax_amount decimal(10, 2)
total_amount decimal(10, 2)
customer_notes text nullable
admin_notes text nullable
placed_at datetime nullable
paid_at datetime nullable
shipped_at datetime nullable
delivered_at datetime nullable
cancelled_at datetime nullable
cancelled_by FK User nullable
cancellation_reason text nullable
created_at datetime
updated_at datetime
```

Indexes:
- order_number.
- customer.
- status.
- payment_status.
- created_at.
- `(customer, created_at)`.

Rules:
- Status transitions must be forward-only except cancellation.
- Customers can cancel only before shipped.
- Admin can cancel according to business policy.

### OrderItem

```txt
id UUID PK
order FK Order
product FK Product
variant FK Variant
product_name string
variant_name string
sku string
quantity integer
unit_price decimal(10, 2)
line_total decimal(10, 2)
created_at datetime
updated_at datetime
```

Indexes:
- order.
- variant.

Notes:
- Product, variant, sku, and price are snapshotted for historical accuracy.

### OrderStatusHistory

```txt
id UUID PK
order FK Order
from_status string nullable
to_status string
changed_by FK User nullable
reason text nullable
created_at datetime
```

Indexes:
- order.
- to_status.
- created_at.

## shipping

### ShippingMethod

```txt
id UUID PK
name string
code string unique
description text nullable
base_price decimal(10, 2)
price_per_kg decimal(10, 2)
estimated_min_days integer
estimated_max_days integer
is_active boolean
created_at datetime
updated_at datetime
```

### OrderShippingAddress

Address snapshot for an order.

```txt
id UUID PK
order FK Order unique
full_name string
phone string
line1 string
line2 string nullable
city string
state string nullable
postal_code string
country string
created_at datetime
updated_at datetime
```

### OrderTracking

```txt
id UUID PK
order FK Order unique
carrier string
tracking_number string unique
tracking_url string nullable
status enum(processing, in_transit, out_for_delivery, delivered, exception)
estimated_delivery date nullable
last_update datetime nullable
created_at datetime
updated_at datetime
```

Indexes:
- order.
- tracking_number.
- status.

## payments

### Payment

```txt
id UUID PK
order FK Order
provider enum(stripe)
provider_payment_intent_id string unique nullable
provider_charge_id string unique nullable
amount decimal(10, 2)
currency string
status enum(pending, succeeded, failed, cancelled)
failure_reason text nullable
metadata json nullable
created_at datetime
updated_at datetime
processed_at datetime nullable
```

Indexes:
- order.
- provider_payment_intent_id.
- status.

### PaymentEvent

Stores webhook events to prevent duplicate processing.

```txt
id UUID PK
provider enum(stripe)
event_id string unique
event_type string
payload json
processed_at datetime nullable
processing_error text nullable
created_at datetime
```

Indexes:
- event_id.
- event_type.
- processed_at.

### Refund

```txt
id UUID PK
payment FK Payment
order FK Order
return_request FK ReturnRequest nullable
provider_refund_id string unique nullable
amount decimal(10, 2)
reason text nullable
status enum(pending, succeeded, failed, cancelled)
created_by FK User nullable
created_at datetime
updated_at datetime
processed_at datetime nullable
```

Indexes:
- payment.
- order.
- return_request.
- status.

## returns

### ReturnRequest

```txt
id UUID PK
return_number string unique
order FK Order
customer FK User
status enum(pending_review, approved, rejected, awaiting_return, in_transit, received, processed, refunded, replaced, completed)
reason enum(damaged, wrong_item, missing_item, defective, other)
resolution enum(refund, replacement, store_credit) nullable
comments text nullable
admin_notes text nullable
rejection_reason text nullable
refund_amount decimal(10, 2) nullable
reviewed_by FK User nullable
reviewed_at datetime nullable
received_at datetime nullable
completed_at datetime nullable
created_at datetime
updated_at datetime
```

Indexes:
- return_number.
- order.
- customer.
- status.
- created_at.

Rules:
- Order must be delivered.
- Request must be inside return window.
- Same order item cannot be returned twice beyond purchased quantity.

### ReturnItem

```txt
id UUID PK
return_request FK ReturnRequest
order_item FK OrderItem
quantity integer
reason enum(damaged, wrong_item, missing_item, defective, other)
condition_notes text nullable
created_at datetime
updated_at datetime
```

Constraints:
- unique `(return_request, order_item)`.
- `quantity > 0`.

### ReturnImage

```txt
id UUID PK
return_request FK ReturnRequest
image string
created_at datetime
```

### ReturnStatusHistory

```txt
id UUID PK
return_request FK ReturnRequest
from_status string nullable
to_status string
changed_by FK User nullable
reason text nullable
created_at datetime
```

## reviews

### Review

```txt
id UUID PK
product FK Product
customer FK User
order_item FK OrderItem unique
rating integer
title string
content text nullable
status enum(pending, approved, rejected)
helpful_count integer
unhelpful_count integer
approved_at datetime nullable
created_at datetime
updated_at datetime
```

Constraints:
- rating between 1 and 5.
- unique order_item.

Indexes:
- product.
- customer.
- status.
- `(product, status)`.

### ReviewImage

```txt
id UUID PK
review FK Review
image string
created_at datetime
```

### ReviewVote

```txt
id UUID PK
review FK Review
customer FK User
vote enum(helpful, unhelpful)
created_at datetime
updated_at datetime
```

Constraints:
- unique `(review, customer)`.

## wishlist

### WishlistItem

```txt
id UUID PK
customer FK User
product FK Product
variant FK Variant nullable
notes text nullable
created_at datetime
updated_at datetime
```

Constraints:
- unique `(customer, product, variant)`.

Indexes:
- customer.
- product.
- created_at.

## notifications

### NotificationPreference

```txt
id UUID PK
user FK User unique
order_updates_email boolean
order_updates_sms boolean
promotions_email boolean
promotions_sms boolean
created_at datetime
updated_at datetime
```

### Notification

```txt
id UUID PK
user FK User
channel enum(email, sms, in_app)
notification_type string
subject string nullable
body text
status enum(pending, sent, failed)
sent_at datetime nullable
error_message text nullable
created_at datetime
updated_at datetime
```

Indexes:
- user.
- channel.
- status.
- created_at.

## analytics

No required database tables for version 1.

Use selectors for:
- sales totals.
- revenue by date range.
- top products.
- order status distribution.
- return rate.
- customer count.

Add materialized snapshots later only if query performance requires it.

## Critical Transaction Boundaries

Use database transactions for:

- checkout and order creation.
- inventory stock decrement.
- order cancellation and stock restoration.
- Stripe webhook payment success handling.
- refund creation and order payment status updates.
- return approval/rejection.
- return received and stock restoration.
- coupon redemption.

## Version 1 Decisions

- Deduct stock at order creation. Restore it if payment expires, order is cancelled, or a return is received and accepted.
- Use JWT in the `Authorization: Bearer <token>` header.
- Use explicit staff permission codes listed in the accounts section.
- Use one coupon per cart/order.
- Use `base_price + (price_per_kg * total_weight)` for shipping when weight is available; otherwise use base price.
- Restore returned stock after warehouse receipt and acceptance.
- Include store credit in the data model as a return resolution, but implement refund and replacement first.
- Store product image URL/path strings first. Add S3 or another object storage adapter later.
