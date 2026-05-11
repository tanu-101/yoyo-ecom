# 🛍 Orders & Checkout System

---

## 🛒 Cart Structure

### Cart Entity

A cart item represents a product variant in the customer's shopping cart:

```
CartItem
├── ID (UUID)
├── Customer (FK to User)
├── Product (FK to Product)
├── Variant (FK to Variant)
├── Quantity (integer)
├── Added At (timestamp)
└── Updated At (timestamp)
```

### Cart Operations

- **Add:** Check stock availability → Create CartItem
- **Edit:** Validate new quantity → Update CartItem
- **Remove:** Delete CartItem → Recalculate cart

**Cart Total = Subtotal - Discounts + Shipping + Taxes**

---

## 🛍 Checkout Flow

### Checkout Steps

1. Review cart items
2. Select/enter shipping address
3. Apply coupons (optional)
4. Review order and confirm
5. Complete payment
6. Order confirmation

---

## 📦 Order Management System

### Order Entity

```
Order
├── ID (UUID)
├── Customer (FK to User)
├── Status (enum)
├── Payment Status (enum)
├── Shipping Address (JSON)
├── Items (OrderItems list)
├── Subtotal (decimal)
├── Discount (decimal)
├── Shipping Cost (decimal)
├── Total (decimal)
├── Created At (timestamp)
├── Updated At (timestamp)
├── Shipped At (timestamp, nullable)
└── Delivered At (timestamp, nullable)
```

### Order Item Entity

```
OrderItem
├── ID (UUID)
├── Order (FK to Order)
├── Product (FK to Product)
├── Variant (FK to Variant)
├── Quantity (integer)
├── Unit Price (decimal)
├── Line Total (decimal)
└── Created At (timestamp)
```

---

## 📊 Order Status Flow

### Status Lifecycle

```
           Pending Payment
                ↓
    (Customer pays via Stripe)
                ↓
        ✓ Order Placed
                ↓
    (Admin marks as processing)
                ↓
           Processing
                ↓
    (Items packed and shipped)
                ↓
            Shipped
                ↓
    (Item delivered to customer)
                ↓
          Delivered
```

### Status Descriptions

| Status | Description | Actions Available |
|--------|-------------|-------------------|
| **Pending Payment** | Order created, awaiting payment | None (wait for payment) |
| **Placed** | Payment confirmed, ready to process | Edit (10 min window), Cancel |
| **Processing** | Order being prepared for shipment | Update tracking |
| **Shipped** | Order dispatched, in transit | View tracking |
| **Delivered** | Order received by customer | Request return, Leave review |

### Status Transition Rules

✅ **Forward-only transitions allowed:**
- Placed → Processing → Shipped → Delivered
- No backward transitions
- No status skipping

❌ **Backward transitions blocked:**
- Cannot go from Shipped → Processing
- Cannot go from Delivered → Shipped
- System enforces forward-only movement

---

## ⏰ Order Edit Policy

### Editable Window

Orders can be **edited within 10 minutes** of placement, subject to conditions:

```
Order Placed: 10:00 AM
├─ 10:05 AM: ✅ Editable (within 10 minutes)
├─ 10:09 AM: ✅ Editable (still within 10 minutes)
└─ 10:11 AM: ❌ Locked (exceeded 10 minutes)
```

### Lock Conditions

Order becomes **locked** when:

1. **Time Exceeded**
   - More than 10 minutes since placement
   - Automatic system check

2. **Status Changes**
   - Status changes to "Processing"
   - Admin initiated processing
   - Locked immediately upon status change

### Locked Behavior

Once locked:
- ❌ Cannot modify items
- ❌ Cannot change quantity
- ❌ Cannot change address
- ✅ Can only cancel (if allowed)

### What Can Be Edited

Before lock, customers can:
- ✅ Modify item quantities
- ✅ Remove items (if cart not empty after removal)
- ✅ Change shipping address
- ✅ Cancel order

---

## ❌ Order Cancellation

### Customer Cancellation

**Eligibility:**
- ✅ Can cancel before order shipped
- ✅ Cannot cancel after "Shipped"
- ✅ Cannot cancel after "Delivered"

**Process:**
```
Customer requests cancellation
  ↓
System validates status
  ↓
If status < "Shipped":
  ├─ Cancel order
  ├─ Restore inventory
  ├─ Initiate refund
  └─ Send confirmation
  
If status >= "Shipped":
  ├─ Deny cancellation
  └─ Suggest return instead
```

### Admin Cancellation

**Eligibility:**
- ✅ Can cancel at any time
- ✅ Any status (except already cancelled)
- ✅ Requires reason/explanation

**Process:**
```
Admin initiates cancellation with reason
  ↓
System validates
  ↓
Order cancelled
  ├─ Restore inventory
  ├─ Initiate refund
  ├─ Log reason
  └─ Notify customer
```

### Cancellation Effects

When order is cancelled:
1. **Inventory Restoration**
   - All reserved stock returned
   - Variant stock increased

2. **Payment Handling**
   - If paid: Refund initiated
   - If pending: Cancelled automatically

3. **Notifications**
   - Customer notified
   - Cancellation reason provided
   - Refund timeline communicated

---

## 💼 Order Timeline Example

```
10:00 AM: Order #ORD-12345 Placed
         Status: Pending Payment
         Items: 1x Red T-Shirt (Size M)
         
10:05 AM: Payment Confirmed (Stripe)
         Status: Order Placed
         
10:15 AM: Admin marks as Processing
         Status: Processing
         Editable: ❌ (locked - status changed)
         
02:00 PM: Admin updates tracking: TRK-98765
         Status: Shipped
         
Next Day: Customer receives package
         Status: Delivered
         Action: Can now request return or leave review
```

---

## 📋 Order View for Customers

Customers can view their orders with:
- ✅ Order ID and date
- ✅ Order status
- ✅ Items and quantities
- ✅ Total amount paid
- ✅ Shipping address
- ✅ Tracking information (when shipped)
- ✅ Return status (if applicable)

---

## 📋 Summary

| Aspect | Details |
|--------|---------|
| **Cart Items** | Product variant + quantity |
| **Checkout Steps** | 6-step process ending in payment |
| **Order Statuses** | 5 stages (Pending → Delivered) |
| **Status Movement** | Forward-only, no backtracking |
| **Edit Window** | 10 minutes or until "Processing" |
| **Customer Cancel** | Before "Shipped" |
| **Admin Cancel** | Anytime with reason |
| **Stock Restoration** | Automatic on cancellation |

---

**Related Documents:**
- [Products & Inventory](./03-PRODUCTS-INVENTORY.md)
- [Payments & Shipping](./05-PAYMENTS-SHIPPING.md)
- [Return Management](./06-RETURNS.md)
- [System Workflows](./08-WORKFLOWS.md)
