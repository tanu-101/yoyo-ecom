# Authentication, Users, And Staff Implementation Plan

## Context

Build the accounts foundation first: JWT auth, customer self-service, admin user management,
staff account management, permission assignment, OTP verification, forgot-password reset,
and user profile image management. This must follow the service/selector architecture so
later commerce modules can reuse the same RBAC behavior.

## Current Status

- Models exist: `User`, `Address`, `StaffPermission`.
- OTP/reset-token model is required for email verification and password reset.
- Constants exist: `UserRole`, `StaffPermissionCode`.
- Service exists only for basic staff permission assignment.
- API folders/routes are scaffolded but serializers/views are empty.
- Therefore auth/user/admin APIs are not functional yet.

## API Scope

### Customer Auth

- `POST /api/v1/customer/auth/register/`
- `POST /api/v1/customer/auth/login/`
- `POST /api/v1/customer/auth/refresh/`
- `POST /api/v1/customer/auth/logout/`
- `GET /api/v1/customer/auth/me/`
- `POST /api/v1/customer/auth/request-email-verification/`
- `POST /api/v1/customer/auth/verify-email/`
- `POST /api/v1/customer/auth/forgot-password/`
- `POST /api/v1/customer/auth/reset-password/`

### Customer Profile

- `GET /api/v1/customer/profile/`
- `PATCH /api/v1/customer/profile/`
- `POST /api/v1/customer/profile/change-password/`
- `PATCH /api/v1/customer/profile/image/`

### Customer Addresses

- `GET /api/v1/customer/addresses/`
- `POST /api/v1/customer/addresses/`
- `GET /api/v1/customer/addresses/{id}/`
- `PATCH /api/v1/customer/addresses/{id}/`
- `DELETE /api/v1/customer/addresses/{id}/`
- `POST /api/v1/customer/addresses/{id}/set-default/`

### Admin Users

- `GET /api/v1/admin/users/`
- `POST /api/v1/admin/users/`
- `GET /api/v1/admin/users/{id}/`
- `PATCH /api/v1/admin/users/{id}/`
- `POST /api/v1/admin/users/{id}/activate/`
- `POST /api/v1/admin/users/{id}/deactivate/`
- `POST /api/v1/admin/users/{id}/soft-delete/`
- `POST /api/v1/admin/users/{id}/reset-password/`
- `POST /api/v1/admin/users/{id}/set-role/`

### Admin Staff

- `GET /api/v1/admin/staff/`
- `POST /api/v1/admin/staff/`
- `GET /api/v1/admin/staff/{id}/`
- `PATCH /api/v1/admin/staff/{id}/`
- `PATCH /api/v1/admin/staff/{id}/permissions/`

## Permission Rules

- Public: register, login, refresh.
- Authenticated: logout, me, profile, own addresses.
- Customer: can manage only own profile and own addresses.
- Admin role: can manage users and staff through admin APIs.
- Superuser: always treated as admin for API authorization.
- Staff: no admin API access unless explicitly allowed by a future staff permission endpoint.
- Admin cannot soft-delete/deactivate their own account through API.
- Admin cannot remove the last active admin/superuser.
- Customers cannot set their role, staff status, superuser status, or verification flags.
- Staff accounts must use `role=staff`; customer registration must force `role=customer`.
- Email verification uses short-lived OTP records and marks `is_email_verified=True`.
- Forgot-password reset uses a separate short-lived OTP purpose and does not log users in.
- Profile image is stored in `User.profile_picture` as a URL/path string for v1.

## Selector Layer

Add or extend `backend/apps/accounts/selectors/users.py`:

- `active_users()`
- `users_list(role=None, is_active=None, search=None, include_deleted=False)`
- `get_user_by_id(user_id, include_deleted=False)`
- `get_active_user_by_email(email)`
- `staff_users(include_inactive=False)`
- `user_permissions(user)`
- `is_last_active_admin(user)`
- `get_valid_otp(user, purpose, code)`

Add `backend/apps/accounts/selectors/addresses.py`:

- `addresses_for_user(user)`
- `get_address_for_user(user, address_id)`
- `default_address_for_user(user)`

## Service Layer

Add `backend/apps/accounts/services/authentication.py`:

- `register_customer(...)`
- `authenticate_user(email, password)`
- `issue_tokens(user)`
- `logout_refresh_token(refresh_token)`
- `change_password(user, old_password, new_password)`
- `request_email_verification(user)`
- `verify_email(user, code)`
- `request_password_reset(email)`
- `reset_password(email, code, new_password)`

Add `backend/apps/accounts/services/users.py`:

- `create_user(...)`
- `create_staff_user(..., permissions)`
- `update_user_profile(user, data)`
- `update_user_profile_image(user, profile_picture)`
- `admin_update_user(actor, target_user, data)`
- `activate_user(actor, target_user)`
- `deactivate_user(actor, target_user)`
- `soft_delete_user(actor, target_user)`
- `reset_user_password(actor, target_user, new_password)`
- `set_user_role(actor, target_user, role)`

Extend `backend/apps/accounts/services/staff_permissions.py`:

- `set_staff_permission(...)`
- `set_staff_permissions(staff_user, permission_updates, granted_by)`
- `enabled_permission_codes(staff_user)`

Add `backend/apps/accounts/services/addresses.py`:

- `create_address(user, data)`
- `update_address(user, address, data)`
- `delete_address(user, address)`
- `set_default_address(user, address)`

## API Layer

Serializers must validate request/response shapes only. Views must call selectors/services only.

- `backend/api/v1/customer/auth/serializers.py`
- `backend/api/v1/customer/auth/views.py`
- `backend/api/v1/customer/auth/urls.py`
- `backend/api/v1/customer/profile/serializers.py`
- `backend/api/v1/customer/profile/views.py`
- `backend/api/v1/customer/profile/urls.py`
- `backend/api/v1/customer/addresses/serializers.py`
- `backend/api/v1/customer/addresses/views.py`
- `backend/api/v1/customer/addresses/urls.py`
- `backend/api/v1/admin/users/serializers.py`
- `backend/api/v1/admin/users/views.py`
- `backend/api/v1/admin/users/urls.py`
- `backend/api/v1/admin/staff/serializers.py`
- `backend/api/v1/admin/staff/views.py`
- `backend/api/v1/admin/staff/urls.py`

## Testing Plan

### Factories

- Add `backend/apps/accounts/factories.py`.
- Factories: `UserFactory`, `AdminUserFactory`, `SuperUserFactory`, `StaffUserFactory`,
  `CustomerUserFactory`, `AddressFactory`, `StaffPermissionFactory`.

### Service Tests

- Customer registration always creates `role=customer`.
- Duplicate email is rejected.
- Login rejects invalid password, inactive users, and soft-deleted users.
- Password change requires the old password.
- Admin can update allowed fields.
- Admin cannot deactivate/soft-delete self.
- Last active admin/superuser cannot be deactivated or soft-deleted.
- Staff permissions can only be assigned to staff users.
- Setting default address unsets the previous default.

### Selector Tests

- User list filters by role, active status, search, and deletion state.
- Staff selectors return only staff users.
- Address selectors only return addresses owned by the user.
- Last-admin detection works for admin-role and superuser accounts.

### API Tests

- Register/login/refresh/logout/me status codes and response shape.
- Email verification request creates an OTP and verify marks user email verified.
- Forgot password creates an OTP and reset password changes the password.
- Profile read/update requires authentication.
- Profile image update stores the image URL/path.
- Address CRUD requires ownership.
- Admin users list/detail/update requires admin or superuser.
- Admin can create customer/staff/admin users only through admin endpoint.
- Admin activation/deactivation/soft-delete/reset-password/set-role endpoints work.
- Superuser can access all admin user/staff endpoints.
- Customer and normal staff receive 403 for admin endpoints.
- Staff permission update validates permission codes and target role.

## Verification Commands

- `python backend/manage.py check`
- `python -m compileall backend`
- `cd backend && ruff check .`
- `cd backend && mypy .`
- `cd backend && pytest apps/accounts api/v1/customer api/v1/admin`

## Guardrails

- No business logic in API views or serializers.
- No direct user/address query logic in API views.
- Never expose password hashes or deleted users by default.
- Never trust frontend role/permission claims.
- Prefer explicit service functions over generic abstractions.
- Keep OTP responses generic where email existence should not be leaked.
