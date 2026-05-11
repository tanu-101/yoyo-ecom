# 🛡 Security Requirements

## 🔐 Authentication (JWT)
The system uses JSON Web Tokens (JWT) for stateless authentication.

### Flow
1.  **Login:** User submits credentials to `POST /api/auth/login/`.
2.  **Token Issuance:** Server validates and returns `access` and `refresh` tokens.
3.  **Authorized Requests:** Client includes `Authorization: Bearer <access_token>` in headers.
4.  **Refresh:** When `access` expires, client uses `refresh` token at `POST /api/auth/refresh/`.

---

## 👥 Authorization (RBAC)
Role-Based Access Control is enforced at the API level using Django permissions.

### Role Hierarchy
1.  **Admin:** Superuser status. Access to all `/api/admin/*` and `/api/management/*` endpoints.
2.  **Staff:** Access to management endpoints restricted by granular flags (e.g., `can_manage_products`, `can_handle_returns`).
3.  **Customer:** Access only to `/api/storefront/*` and own profile/orders.

### Permission Mapping Table
| Resource | Action | Required Role/Permission |
|----------|--------|--------------------------|
| Product | Create/Edit | Admin OR Staff (can_manage_products) |
| Order | Update Status | Admin OR Staff (can_process_orders) |
| Order | View Own | Customer (Owner) |
| Return | Approve | Admin Only |
| Analytics | View | Admin Only |

---

## 🛡 API Security

### Rate Limiting
To prevent Brute Force and DoS attacks:
- **Auth Endpoints:** 5 requests per minute per IP.
- **Product Search:** 60 requests per minute per IP.
- **Standard API:** 1000 requests per hour per authenticated user.

### Webhook Security (Stripe)
- **Signature Verification:** All incoming Stripe webhooks must be verified using the `STRIPE_WEBHOOK_SECRET`.
- **Idempotency:** The system tracks `Stripe-Event-ID` to prevent processing the same payment multiple times.

### Data Protection
- **Input Validation:** All API inputs are validated using DRF Serializers to prevent SQL Injection and XSS.
- **CORS:** Only approved domains (e.g., `production-frontend.com`) can make cross-origin requests.
- **Secrets Management:** Sensitive keys (Stripe Secret, JWT Secret, DB Credentials) are stored in environment variables, never in code.

---

## 📋 Security Checklist for Developers
- [ ] Never log JWT tokens or passwords.
- [ ] Use `is_authenticated` permission for all non-public endpoints.
- [ ] Ensure `select_for_update()` is used inside transactions for inventory.
- [ ] Sanitize all user-generated content (reviews).
- [ ] Regularly rotate API keys and secrets.

---

**Related Documents:**
- [User Roles & Permissions](./02-USER-ROLES.md)
- [System Architecture](./01-ARCHITECTURE.md)
