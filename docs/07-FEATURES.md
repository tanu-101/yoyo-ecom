# ✨ Additional Features

## 🔍 Search & Filtering System

### Implementation Details
- **Engine:** PostgreSQL Full-Text Search (using GIN indexes).
- **Searchable Fields:** Product `name`, `description`, and Category `name`.
- **Ranking:** Weighted results where `name` matches rank higher than `description`.

### Optimization
```sql
-- GIN index for fast text search
CREATE INDEX idx_product_search ON products USING GIN (to_tsvector('english', name || ' ' || description));
```

### Advanced Filters
- **Dynamic Facets:** Available filters (Size, Color) update based on the current search result set.
- **Price Range:** Aggregated min/max prices calculated per category.

---

## ❤️ Wishlist System

### Logic & Persistence
- **Storage:** Database-level persistence for authenticated users.
- **Sync:** Real-time synchronization across devices via API.
- **Variant Support:** Users can wishlist specific variants (e.g., Red - Size M).

### Wishlist Entity Schema
```python
class WishlistItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
```

---

## ⭐ Review & Rating System

### Business Rules
1.  **Verified Purchase:** Only customers with a `Delivered` order status for the specific product can leave a review.
2.  **One per Item:** Limit of one review per product per user.
3.  **Cool-down:** Reviews allowed 24 hours after delivery to ensure genuine feedback.

### Moderation Workflow
- **State Machine:** `Pending` → `Approved` | `Rejected`.
- **Automation:** Automatic flagging of reviews containing blacklisted keywords or repetitive patterns (spam).

---

## 🔔 Notification System

### Notification Matrix
| Event | Channel | Priority | Trigger |
|-------|---------|----------|---------|
| Order Placed | Email | High | Payment Webhook Success |
| Order Shipped | Email/SMS| Medium | Admin status update |
| Low Stock | Admin Alert| Medium | Inventory falls below threshold |
| Return Approved| Email | High | Admin approval |

### Technical Stack
- **Provider:** Twilio (SMS), SendGrid/AWS SES (Email).
- **Queueing:** Celery + Redis for asynchronous message delivery.

---

## ⚙️ Admin & Analytics

### Control Panel
- **RBAC Integration:** Admin interface visibility is restricted by staff permissions.
- **Bulk Operations:** CSV import for products and bulk stock updates.

### Analytics Engine
- **Aggregations:** Real-time sales calculations using Django `Sum` and `Count` aggregates.
- **Metrics:**
    - **AOV (Average Order Value)**
    - **Retention Rate** (Repeat vs New customers)
    - **Product Velocity** (How fast variants sell out)

---

**Related Documents:**
- [User Roles & Permissions](./02-USER-ROLES.md)
- [System Workflows](./08-WORKFLOWS.md)
- [Database Schema](./09-DATABASE.md)
