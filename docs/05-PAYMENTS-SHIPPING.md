# 💳 Payments & Shipping

---

## 💳 Payment System

### Payment Flow Overview

```
Order Created
    ↓
Status: Pending Payment
    ↓
Customer Initiates Payment
    ↓
Stripe Payment Gateway
    ↓
Payment Processed
    ↓
Stripe Webhook Sent
    ↓
System Updates Order Status
    ↓
Order Processing Begins
```

---

## 💰 Payment Process

1. Customer completes checkout → Order created with status "Pending Payment"
2. Customer clicks "Pay Now" → Redirected to Stripe payment form
3. Stripe processes payment → Sends webhook with confirmation
4. System verifies webhook signature → Updates order status
5. Order status: Pending Payment → Placed
6. Order enters processing queue

**Status Transitions:**
- Pending → Paid → Processing
- Pending → Failed → Retry

---

## 📊 Payment Status States

### Payment Status Lifecycle

```
         Pending
            ↓
    (Stripe processes)
            ↓
        ✓ Paid
            ↓
    (Order processing)
            ↓
         Delivered
            ↓
    (if return requested)
            ↓
        Refunded
```

### Status Definitions

| Status | Meaning | Next Action |
|--------|---------|-------------|
| **Pending** | Awaiting payment completion | Process payment |
| **Paid** | Payment received and verified | Process order |
| **Failed** | Payment declined or failed | Retry payment |
| **Refunded** | Full refund issued | Restore inventory |

### Payment Failures

```
Payment Failed
  ↓
Stripe sends failure webhook
  ↓
Order status: Pending Payment (remains)
  ↓
System sends error notification
  ↓
Customer can retry payment
  ↓
Order expires after 24 hours if unpaid
```

---

## 🔒 Payment Security

### Webhook Verification

**Stripe signature verification:**
```python
# Pseudo-code
stripe_signature = request.headers['stripe-signature']
webhook_secret = settings.STRIPE_WEBHOOK_SECRET

try:
    event = stripe.Webhook.construct_event(
        payload=request.body,
        sig_header=stripe_signature,
        secret=webhook_secret
    )
    # Valid webhook - process it
except ValueError:
    # Invalid signature
    return HttpResponse(status=400)
```

### Security Measures

✅ **Signature Verification**
- Verify Stripe signature on every webhook
- Prevent man-in-the-middle attacks
- Use secret webhook endpoint

✅ **Idempotency**
- Prevent duplicate processing
- Check payment ID before recording
- Ensure one-time transactions

✅ **Audit Trail**
- Log all payment events
- Track webhook receipts
- Maintain payment history

✅ **PCI Compliance**
- Never store full card numbers
- Use Stripe tokenization
- Follow PCI DSS standards

---

## 🚚 Shipping & Delivery

### Shipping Address

**Captured at Checkout:**
```
Shipping Address:
├── Full Name
├── Street Address
├── City
├── State/Province
├── Postal Code
├── Country
└── Phone Number
```

### Delivery Charges

**Calculated based on:**
- Order weight
- Shipping destination
- Shipping method (Standard, Express, Overnight)
- Current location
- Distance from warehouse

**Example:**
```
Order Weight: 2 kg
Destination: Los Angeles, CA
Method: Standard Shipping

Standard Rate: $5 base + $0.50/kg
Total: $5 + (2 × $0.50) = $6
```

### Shipping Methods

| Method | Delivery Time | Cost | Use Case |
|--------|---------------|------|----------|
| **Standard** | 5-7 business days | Base rate | Regular orders |
| **Express** | 2-3 business days | Base + $5 | Rush orders |
| **Overnight** | Next business day | Base + $15 | Urgent orders |

---

## 📍 Tracking System

### Tracking ID Assignment

```
Order marked as "Shipped"
  ↓
Admin provides tracking ID
  └─ From shipping provider (FedEx, UPS, etc.)
  ↓
Tracking ID saved to order
  ↓
Customer notified with tracking link
```

### Customer Tracking

**Customers can:**
- ✅ View tracking ID
- ✅ Click tracking link
- ✅ View real-time package location
- ✅ See estimated delivery date
- ✅ Receive delivery notifications

**Tracking States:**
```
Tracking States (from provider)
├── Processing: Package at facility
├── In Transit: On the way
├── Out for Delivery: Arriving today
├── Delivered: Successfully delivered
└── Exception: Delayed or issue
```

---

## 📦 Order Processing Stages

### Stage 1: Order Placed

```
Status: Placed
├─ Payment confirmed
├─ Inventory locked
├─ Ready for processing
└─ Duration: 0-24 hours
```

### Stage 2: Processing

```
Status: Processing
├─ Order assigned to fulfillment
├─ Items picked from inventory
├─ Items packed in box
├─ Quality check performed
└─ Duration: 1-2 business days
```

### Stage 3: Shipped

```
Status: Shipped
├─ Package handed to carrier
├─ Tracking ID assigned
├─ Customer notified
├─ In transit to destination
└─ Duration: 2-7 business days (depending on method)
```

### Stage 4: Delivered

```
Status: Delivered
├─ Package at customer location
├─ Signature/confirmation collected
├─ Customer notified
├─ Return window starts
└─ Customer can review/rate product
```

---

## 🔄 Delivery Status Updates

### Automatic Updates

System receives updates from shipping provider:
```
Every 24-48 hours
  ↓
Poll shipping provider API
  ↓
If status changed:
├─ Update order status
├─ Send customer notification
└─ Update tracking info
```

### Manual Updates (Admin)

Admin can manually update:
```
Admin marks order as "Shipped"
  ↓
Enters tracking ID
  ↓
System updates order
  ├─ Status: Processing → Shipped
  ├─ Tracking ID stored
  └─ Customer notified
```

---

## 📧 Shipping Notifications

### Email Notifications Sent

1. **Order Confirmed**
   - When payment received
   - Order details included
   - Estimated delivery date

2. **Order Shipped**
   - When order marked shipped
   - Tracking ID included
   - Tracking link provided

3. **Out for Delivery**
   - When package out for delivery
   - Estimated delivery window
   - Delivery instructions

4. **Delivered**
   - When package delivered
   - Request for review/rating
   - Return instructions (if eligible)

---

## 🏢 Warehouse Management

### Fulfillment Process

```
Order Placed (Status: Processing)
  ↓
Print picking slip
  ↓
Locate items in warehouse
  ↓
Pick items from shelves
  ↓
Quality check (verify correct items)
  ↓
Pack items securely
  ↓
Apply shipping label
  ↓
Hand off to carrier
  ↓
Mark order as "Shipped"
  ↓
Generate tracking ID
  ↓
Send to customer
```

---

## 📋 Summary

| Aspect | Details |
|--------|---------|
| **Payment Gateway** | Stripe integration |
| **Webhook Verification** | Signature-based validation |
| **Duplicate Prevention** | Idempotency checks |
| **Shipping Address** | Captured at checkout |
| **Delivery Charges** | Weight and distance based |
| **Tracking** | Real-time package tracking |
| **Notifications** | Email at key milestones |
| **Delivery Stages** | Processing → Shipped → Delivered |

---

**Related Documents:**
- [Orders & Checkout](./04-ORDERS-CHECKOUT.md)
- [Return Management](./06-RETURNS.md)
- [System Workflows](./08-WORKFLOWS.md)
- [Security Requirements](./10-SECURITY.md)
