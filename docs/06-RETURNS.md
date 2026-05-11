# 🔁 Return Management System

---

## 📋 Return Eligibility

**Allowed:** Damaged product, wrong item delivered, missing item, product defects
**Not Allowed:** Customer-caused damage, "changed mind" (outside window), items before delivery, returns after 7 days
**Window:** 7 days from delivery date

---

## 🔄 Return Workflow

1. Customer submits return request → Select reason (Damaged, Wrong Item, Missing, Other) → Add comments/photos (optional)
2. System validates: Order delivered, within 7-day window, reason valid, not already returned
3. Admin reviews request → Approve or reject with reason
4. If approved: Generate shipping label → Send to customer → Customer ships item
5. Admin receives item → Inspect condition → Approve/reject return
6. Process resolution: Issue refund (full/partial) or send replacement
7. Update order status → Send confirmation email
└─ All checks pass ✓
  ↓
System creates ReturnRequest record
  │
  ├─ Status: "Pending Review"
  └─ Assigned to: Admin queue
```

### Step 3: Admin Review

```
Admin receives return request
  ↓
Admin reviews:
├─ Order details
├─ Product photos
├─ Customer comments
├─ Return reason
└─ Historical returns by customer
  ↓
Admin decision:
├─ Approve → Process refund/replacement
└─ Reject → Provide reason
```

### Step 4a: Approved Return

```
Admin clicks "Approve"
  ↓
Determines resolution:
├─ Option 1: Refund to payment method
├─ Option 2: Replacement order
├─ Option 3: Store credit
└─ (Customer may have preference)
  ↓
Generates return shipping label
  ↓
Customer notified:
├─ Approval confirmed
├─ Refund/replacement details
├─ Return shipping instructions
└─ Tracking for return shipment
  ↓
Status: "Approved"
```

### Step 4b: Rejected Return

```
Admin clicks "Reject"
  ↓
Selects rejection reason:
├─ Outside return window
├─ Customer-caused damage
├─ Invalid reason
└─ Other (with explanation)
  ↓
Adds explanatory message
  ↓
Customer notified:
├─ Rejection confirmed
├─ Detailed reason
├─ Explanation
└─ Appeal instructions (if applicable)
  ↓
Status: "Rejected"
```

---

## 🔀 Return Resolution Options

### Option 1: Refund

```
Approved → Refund Selected
  ↓
System initiates refund to:
├─ Original payment method (if possible)
├─ Store credit (if card no longer valid)
└─ Other method (if requested)
  ↓
Refund timeline: 5-10 business days
  ↓
Customer receives funds
  ├─ Payment method confirmation
  └─ Refund amount
  ↓
Stock Restored: ✅
└─ Variant stock increased by return quantity
```

### Option 2: Replacement

```
Approved → Replacement Selected
  ↓
System creates new order:
├─ Same product, different variant (if applicable)
├─ Or same product & variant
├─ Shipping to same address
└─ No charge to customer
  ↓
Replacement shipped
  ↓
Stock Changes:
├─ Original variant: Restored
└─ Replacement variant: Reserved
```

### Option 3: Store Credit

```
Approved → Store Credit Selected
  ↓
System creates store credit account:
├─ Credit amount = Original order total
├─ Valid for future purchases
├─ Expires after 1 year (if applicable)
└─ Non-refundable to cash
  ↓
Customer notified with credit details
  ↓
Can use for next purchase
```

---

## 📊 Return Status Flow

```
          Pending Review
                ↓
    (Admin reviews and decides)
                ↓
        ┌───────┴───────┐
        ↓               ↓
     Approved        Rejected
        ↓               ↓
    Awaiting Return  Complete
        ↓
    In Transit
        ↓
    Received
        ↓
    Processed
        ↓
    Refunded/Replaced
        ↓
    Complete
```

---

## 📦 Return Shipping

### Return Label Generation

```
Admin approves return
  ↓
System generates return shipping label
  ↓
Label includes:
├─ Return address (warehouse)
├─ Tracking number
├─ QR code
└─ Customer info
  ↓
Label sent to customer via email
  ↓
Customer prints label
  ↓
Attaches to package
  ↓
Drops at carrier location
```

### Return Tracking

```
Customer ships return package
  ↓
Tracking updates from carrier
  ↓
System monitors tracking:
├─ In Transit
├─ Out for Delivery
└─ Delivered to Warehouse
  ↓
When delivered:
├─ Status: "Received"
├─ Warehouse inspects item
└─ Processes refund/replacement
```

---

## 💰 Refund Processing

### Refund Timeline

```
Return Approved: May 10
  ├─ Customer ships return (May 10-15)
  │
  ├─ Return arrives at warehouse (May 20)
  │
  ├─ Warehouse processes (May 21-22)
  │   └─ Inspects item
  │   └─ Verifies condition
  │
  ├─ Refund initiated (May 22)
  │   └─ Payment system processes
  │
  └─ Refund received by customer (May 27-29)
       └─ 5-10 business days
```

### Refund Amount

```
Refund Amount = Order Total - (Shipping + Restocking Fee if applicable)

Example 1: Damaged in Shipping
├─ Product: $50
├─ Shipping: $5
├─ Restocking: $0 (not customer fault)
└─ Refund: $55

Example 2: Wrong Item
├─ Product: $50
├─ Shipping: $5
├─ Restocking: $0 (not customer fault)
└─ Refund: $55

Example 3: Customer Changed Mind (if allowed)
├─ Product: $50
├─ Shipping: $5
├─ Restocking: $5 (customer caused)
└─ Refund: $45
```

---

## 📊 Return Analytics

### Admin Dashboard Metrics

- **Total Returns:** By month/year
- **Return Rate:** Returns / Orders %
- **Top Return Reasons:** Ranked by frequency
- **Return Products:** Which products return most
- **Customer Returns:** Patterns and repeat returners
- **Resolution Types:** Refund vs Replacement breakdown
- **Refund Amounts:** Total refunded vs revenue

### Quality Insights

```
High Return Rate on Product X?
  ├─ Review quality issues
  ├─ Adjust product description
  ├─ Reach out to supplier
  └─ Consider discontinuation
```

---

## 🚨 Exception Cases

### Edge Case 1: Item Lost in Return Shipping

```
Customer ships return
  ↓
Tracking shows "Delivered"
  ↓
Warehouse: "Not received"
  ↓
Action:
├─ Investigate with carrier
├─ Request proof of delivery
├─ Process refund if carrier liable
└─ Notify customer
```

### Edge Case 2: Item Arrived Damaged

```
Customer ships return
  ↓
Warehouse receives damaged item
  ↓
Inspection: Item more damaged than original return
  ↓
Action:
├─ Contact customer with photos
├─ Offer reduced refund
├─ Or deny return
└─ Notify customer of resolution
```

### Edge Case 3: Fraudulent Return

```
Customer returns different item
  ├─ Original: Red Shirt
  ├─ Returned: Blue Shirt
  ↓
Warehouse detects discrepancy
  ↓
Action:
├─ Flag account for fraud
├─ Contact customer to clarify
├─ Request correct item
├─ Or deny return + keep payment
└─ Monitor for future issues
```

---

## 📋 Return Request Data

### ReturnRequest Entity

```
ReturnRequest
├── ID (UUID)
├── Order (FK to Order)
├── OrderItem (FK to OrderItem)
├── Customer (FK to User)
├── Status (enum)
├── Reason (enum)
├── Comments (text)
├── Photos (JSON array of URLs)
├── Resolution (refund/replacement/credit)
├── Admin Notes (text)
├── Created At (timestamp)
├── Reviewed At (timestamp, nullable)
├── Completed At (timestamp, nullable)
└── Refund Amount (decimal, nullable)
```

---

## 📋 Summary

| Aspect | Details |
|--------|---------|
| **Allowed Returns** | Damaged, Wrong Item, Missing Item |
| **Not Allowed** | Customer damage, Outside window, Invalid reason |
| **Return Window** | 7 days after delivery |
| **Status Flow** | Pending → Approved/Rejected → Processed |
| **Resolutions** | Refund, Replacement, Store Credit |
| **Refund Timeline** | 5-10 business days after received |
| **Stock Handling** | Restored on approval |
| **Tracking** | Customer tracks return shipment |

---

**Related Documents:**
- [Orders & Checkout](./04-ORDERS-CHECKOUT.md)
- [Payments & Shipping](./05-PAYMENTS-SHIPPING.md)
- [System Workflows](./08-WORKFLOWS.md)
- [Database Schema](./09-DATABASE.md)
