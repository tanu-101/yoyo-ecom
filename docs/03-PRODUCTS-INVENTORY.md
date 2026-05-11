# 🛒 Products & Inventory Management

---

## 📦 Product Structure

### Product Entity

A product is the main catalog item with the following attributes:

```
Product
├── ID (UUID)
├── Name (string)
├── Description (text)
├── Category (FK to Category)
├── Base Price (decimal)
├── Status (active/inactive)
├── Created At (timestamp)
└── Updated At (timestamp)
```

### Variant Entity

Products support variants for different configurations (e.g., size, color):

```
Variant
├── ID (UUID)
├── Product (FK to Product)
├── Name (string, e.g., "Red - Size M")
├── Type (string, e.g., "Color", "Size")
├── Price (decimal - overrides base price)
├── Stock (integer)
├── Status (available/unavailable)
├── Created At (timestamp)
└── Updated At (timestamp)
```

### Variant vs Product

**Product Example:**
- Name: "T-Shirt"
- Base Price: $20
- Variants:
  - Red Size S - $20 (Stock: 10)
  - Red Size M - $20 (Stock: 5)
  - Blue Size S - $22 (Stock: 8)
  - Blue Size M - $22 (Stock: 3)

---

## 📊 Inventory Management

### Inventory Model

Inventory is **only managed at the variant level**, not at the product level.

### Stock Calculation

**Product stock = Sum of all variant stocks**

Example: T-Shirt has Red S (10) + Red M (5) + Blue S (8) + Blue M (3) = 26 total

Stock updates only for selected variant. Other variants unaffected.

---

## 🔒 Inventory Rules

### Rule 1: Prevent Overselling
- ✅ Validate stock before order confirmation
- ✅ Reject orders if stock insufficient
- ✅ Show real-time availability to customers

### Rule 2: Stock Allocation
- ✅ Stock decreases only for selected variant
- ✅ No cross-variant stock sharing
- ✅ Per-variant inventory tracking

### Rule 3: Concurrency Control
- ✅ Use database-level locking
- ✅ Prevent race conditions
- ✅ Ensure data consistency

### Rule 4: Stock Restoration
- ✅ Restore stock when order cancelled
- ✅ Restore stock when order refunded
- ✅ Track restoration history

---

## 🔄 Inventory Update Workflow

### During Order Placement

```
1. Check Variant Stock
   └─ Is stock >= order quantity?
   
2a. If YES:
    ├─ Lock variant row (SELECT FOR UPDATE)
    ├─ Verify stock again (prevent race condition)
    ├─ Reduce stock by order quantity
    ├─ Create inventory transaction log
    └─ Commit transaction
   
2b. If NO:
    ├─ Release lock
    ├─ Block order
    └─ Return error to customer
```

### Concurrency Control Mechanism

**Database Locking (select_for_update):**

```python
# Pseudo-code
variant = Variant.objects.select_for_update().get(id=variant_id)

if variant.stock >= order_quantity:
    variant.stock -= order_quantity
    variant.save()
    transaction.commit()
else:
    transaction.rollback()
    raise OutOfStockError()
```

**Benefits:**
- Prevents double-booking
- Ensures atomicity
- Handles concurrent requests safely
- No race conditions

---

## 📉 Stock Depletion Scenarios

### Scenario 1: Sufficient Stock
```
Variant: "Red Size M"
Current Stock: 5 units
Customer Order: 1 unit

Result:
  ✅ Order Approved
  Stock: 5 → 4 units
```

### Scenario 2: Exact Quantity
```
Variant: "Red Size M"
Current Stock: 1 unit
Customer Order: 1 unit

Result:
  ✅ Order Approved
  Stock: 1 → 0 units (out of stock)
```

### Scenario 3: Insufficient Stock
```
Variant: "Red Size M"
Current Stock: 3 units
Customer Order: 5 units

Result:
  ❌ Order Rejected
  Message: "Only 3 units available"
  Stock: Unchanged (3 units)
```

---

## 🔁 Stock Restoration

### When Stock is Restored

1. **Order Cancellation**
   - Customer cancels before "Shipped"
   - Admin cancels anytime
   - Stock: Reduced → Previous Level

2. **Order Refund**
   - Full refund issued
   - Stock: Reduced → Previous Level

3. **Return Approved**
   - Return request approved
   - Replacement order: Stock allocated
   - Refund order: Stock → Previous Level

### Restoration Logic

```
Order placed: Variant Stock 10 → 9 (1 unit reserved)
Customer cancels within 10 minutes
Restoration triggered: Variant Stock 9 → 10
```

---

## 📊 Inventory Optimization

### Database Indexing

Performance optimization through strategic indexing:

```sql
-- Index on variant availability lookups
CREATE INDEX idx_variant_product_stock 
ON variants(product_id, stock);

-- Index on product name search
CREATE INDEX idx_product_name 
ON products(name);

-- Index on category queries
CREATE INDEX idx_product_category 
ON products(category_id);
```

### Query Optimization

- Bulk fetch variants with stock > 0
- Cache product catalog
- Use select_related for variant-product joins
- Implement pagination for inventory lists

---

## 🎯 Admin Features

### Stock Management
- ✅ View real-time stock levels
- ✅ Manually adjust stock
- ✅ Set low-stock alerts
- ✅ View stock history

### Product Management
- ✅ Create/edit/delete products
- ✅ Create/manage variants
- ✅ Upload product images
- ✅ Manage categories
- ✅ Set pricing and discounts

### Bulk Operations
- ✅ Bulk import products (CSV)
- ✅ Bulk update prices
- ✅ Bulk adjust inventory
- ✅ Bulk status changes

---

## 📋 Summary

| Aspect | Details |
|--------|---------|
| **Stock Level** | Managed at variant level |
| **Product Stock** | Calculated dynamically |
| **Update Mechanism** | Direct quantity adjustment |
| **Concurrency Control** | Database-level locking |
| **Overselling Prevention** | Validation + Locking |
| **Stock Restoration** | On cancellation/refund |
| **Optimization** | Strategic indexing |

---

**Related Documents:**
- [Orders & Checkout](./04-ORDERS-CHECKOUT.md)
- [Database Schema](./09-DATABASE.md)
- [System Workflows](./08-WORKFLOWS.md)
