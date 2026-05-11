# 👥 User Roles & Permissions (RBAC)

---

## 📋 Roles Overview

The system implements three distinct user roles:

| Role | Level | Scope | Purpose |
|------|-------|-------|---------|
| **Admin** | Highest | Full system | Complete system control |
| **Staff** | Medium | Configurable | Delegated operations |
| **Customer** | Lowest | Personal | Shopping and account management |

---

## 🔑 Admin Role

### Access Level
Full system access with no restrictions.

### Permissions
- **Products:** Create, edit, delete, manage variants, pricing
- **Inventory:** View/adjust stock, set alerts
- **Orders:** View all, modify status, cancel anytime, process refunds
- **Returns:** Review, approve/reject, process refunds
- **Users:** Manage staff accounts, assign roles, reset passwords
- **Analytics:** Full access to reports
- **Configuration:** System settings, payment methods, return policies

---

## 👤 Staff Role

### Access Level
Limited, configurable permissions set by Admin.

### Configurable Permissions
- **Products:** Create/edit products (❌ Cannot delete, set prices)
- **Orders:** View/update status (❌ Cannot cancel, modify)
- **Support:** View customers, respond to inquiries (❌ Cannot delete accounts)

### Restrictions
- Access disabled by default
- Admin must explicitly grant each permission
- Permissions can be revoked anytime

---

## 🛍 Customer Role

### Access Level
Personal account and shopping features.

### Core Permissions

- **Account:** Register, login, update profile, change password, delete
- **Shopping:** Browse, search, filter, view details and reviews
- **Cart:** Add/edit/remove items, apply coupons, checkout
- **Orders:** View/track personal orders, cancel (before shipped)
- **Returns:** Request returns, view status, receive refunds
- **Wishlist:** Add/remove items, move to cart, share
- **Reviews:** Rate products (1-5), write reviews (after delivery), edit own
- **Addresses:** Create/edit/delete addresses, set default

---

## 🔄 RBAC Logic

**Permission Determined By:**
1. **User Role** - Base access level
2. **Assigned Permissions** - Fine-grained controls (for Staff)
3. **Data Ownership** - Access to own/assigned/all data

**Rules:**
- ✅ Staff access disabled by default, explicitly granted by Admin
- ✅ Permissions can be enabled/disabled independently
- ✅ Admin can revoke permissions anytime
- ❌ Staff cannot escalate own permissions
- ❌ Customers cannot access other users' data

---

## 📊 Permission Matrix

### Comprehensive Permission Table

| Feature | Admin | Staff | Customer |
|---------|-------|-------|----------|
| **Products** |
| Create Product | ✅ | ⚙️ | ❌ |
| Edit Product | ✅ | ⚙️ | ❌ |
| Delete Product | ✅ | ❌ | ❌ |
| View Products | ✅ | ✅ | ✅ |
| **Orders** |
| View All Orders | ✅ | ⚙️ | ❌ |
| View Own Orders | ✅ | ✅ | ✅ |
| Create Order | ✅ | ❌ | ✅ |
| Edit Order | ✅ | ⚙️ | ⚠️* |
| Cancel Order | ✅ | ❌ | ⚠️* |
| Update Status | ✅ | ⚙️ | ❌ |
| **Returns** |
| View All Returns | ✅ | ⚙️ | ❌ |
| View Own Returns | ✅ | ✅ | ✅ |
| Approve Return | ✅ | ❌ | ❌ |
| Request Return | ✅ | ❌ | ✅ |
| **Inventory** |
| View Stock | ✅ | ⚙️ | ❌ |
| Adjust Stock | ✅ | ❌ | ❌ |
| **Users** |
| Manage Staff | ✅ | ❌ | ❌ |
| Manage Customers | ✅ | ❌ | ❌ |
| **Analytics** |
| View All Analytics | ✅ | ❌ | ❌ |
| View Personal Analytics | ✅ | ❌ | ✅ |

**Legend:**
- ✅ = Allowed
- ❌ = Not allowed
- ⚙️ = Configurable by Admin
- ⚠️* = Limited (time-based restrictions apply)

---

## 🔒 Implementation Guidelines

### Backend Implementation

1. **Permission Decorators**
   ```python
   @require_role('admin')
   @require_permission('manage_products')
   def manage_product(request):
       pass
   ```

2. **Queryset Filtering**
   ```python
   # Customers see only their orders
   if user.is_customer:
       orders = Order.objects.filter(customer=user)
   
   # Staff see assigned orders
   if user.is_staff:
       orders = Order.objects.filter(staff_assigned=user)
   
   # Admin sees all
   if user.is_admin:
       orders = Order.objects.all()
   ```

3. **Permission Validation**
   - Always validate permissions server-side
   - Never rely on frontend-only checks
   - Log permission denials

### Frontend Implementation

1. **Conditional Rendering**
   - Show/hide features based on user role
   - Disable buttons without permissions
   - Show permission denied messages

2. **API Integration**
   - Respect API response codes (403 Forbidden)
   - Handle permission errors gracefully
   - Provide helpful error messages

---

## 📋 Summary

| Role | Access | Use Case |
|------|--------|----------|
| **Admin** | Full system | System management, business operations |
| **Staff** | Configurable | Delegated tasks, customer support |
| **Customer** | Personal scope | Shopping, account management |

---

**Related Documents:**
- [System Architecture](./01-ARCHITECTURE.md)
- [System Workflows](./08-WORKFLOWS.md)
- [Security Requirements](./10-SECURITY.md)
