from __future__ import annotations

import pytest
from django.core import mail

from apps.accounts.constants import StaffPermissionCode, UserRole
from apps.accounts.models import Address, StaffPermission, User
from apps.accounts.tests.helpers import create_user, extract_otp_code

pytestmark = pytest.mark.django_db


def test_customer_register_login_and_me(api_client):
    response = api_client.post(
        "/api/v1/customer/auth/register/",
        {
            "email": "customer@example.com",
            "password": "StrongPass123!",
            "first_name": "Jane",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["data"]["role"] == UserRole.CUSTOMER

    response = api_client.post(
        "/api/v1/customer/auth/login/",
        {"email": "customer@example.com", "password": "StrongPass123!"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["data"]["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['data']['access']}")

    response = api_client.get("/api/v1/customer/auth/me/")

    assert response.status_code == 200
    assert response.data["data"]["email"] == "customer@example.com"


def test_email_verification_uses_otp(api_client):
    user = create_user(email="verify@example.com")
    api_client.force_authenticate(user=user)

    response = api_client.post("/api/v1/customer/auth/request-email-verification/")

    assert response.status_code == 200
    assert len(mail.outbox) == 1

    code = extract_otp_code(mail.outbox[0].body)
    response = api_client.post("/api/v1/customer/auth/verify-email/", {"code": code}, format="json")

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_email_verified is True


def test_forgot_password_resets_password(api_client):
    user = create_user(email="reset@example.com", password="OldStrongPass123!")

    response = api_client.post(
        "/api/v1/customer/auth/forgot-password/",
        {"email": user.email},
        format="json",
    )

    assert response.status_code == 200
    code = extract_otp_code(mail.outbox[0].body)

    response = api_client.post(
        "/api/v1/customer/auth/reset-password/",
        {"email": user.email, "code": code, "new_password": "NewStrongPass123!"},
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("NewStrongPass123!")


def test_profile_image_update(api_client):
    user = create_user(email="profile@example.com")
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        "/api/v1/customer/profile/image/",
        {"profile_picture": "https://example.com/avatar.png"},
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.profile_picture == "https://example.com/avatar.png"


def test_customer_addresses_are_owned_and_defaulted(api_client):
    user = create_user(email="address@example.com")
    other = create_user(email="other@example.com")
    api_client.force_authenticate(user=user)

    first = Address.objects.create(
        user=user,
        full_name="Jane",
        phone="123",
        line1="Line 1",
        city="Dhaka",
        postal_code="1207",
        country="BD",
        is_default=True,
    )
    other_address = Address.objects.create(
        user=other,
        full_name="Other",
        phone="123",
        line1="Line 1",
        city="Dhaka",
        postal_code="1207",
        country="BD",
    )

    response = api_client.post(
        "/api/v1/customer/addresses/",
        {
            "full_name": "Jane Doe",
            "phone": "123",
            "line1": "Line 2",
            "city": "Dhaka",
            "postal_code": "1207",
            "country": "BD",
            "is_default": True,
        },
        format="json",
    )

    assert response.status_code == 201
    first.refresh_from_db()
    assert first.is_default is False

    response = api_client.get(f"/api/v1/customer/addresses/{other_address.id}/")

    assert response.status_code == 404


def test_admin_and_superuser_can_manage_users_but_customer_cannot(api_client):
    customer = create_user(email="customer-admin-test@example.com")
    admin = create_user(email="admin@example.com", role=UserRole.ADMIN)
    superuser = create_user(email="root@example.com", is_superuser=True)

    api_client.force_authenticate(user=customer)
    response = api_client.get("/api/v1/admin/users/")
    assert response.status_code == 403

    api_client.force_authenticate(user=admin)
    response = api_client.get("/api/v1/admin/users/")
    assert response.status_code == 200

    api_client.force_authenticate(user=superuser)
    response = api_client.post(
        "/api/v1/admin/users/",
        {
            "email": "created@example.com",
            "password": "StrongPass123!",
            "role": UserRole.CUSTOMER,
        },
        format="json",
    )
    assert response.status_code == 201


def test_admin_creates_staff_and_updates_permissions(api_client):
    admin = create_user(email="permission-admin@example.com", role=UserRole.ADMIN)
    api_client.force_authenticate(user=admin)

    response = api_client.post(
        "/api/v1/admin/staff/",
        {
            "email": "staff@example.com",
            "password": "StrongPass123!",
            "permissions": [StaffPermissionCode.ORDERS_VIEW],
        },
        format="json",
    )

    assert response.status_code == 201
    staff = User.objects.get(email="staff@example.com")
    assert staff.role == UserRole.STAFF
    assert StaffPermission.objects.filter(
        user=staff,
        permission_code=StaffPermissionCode.ORDERS_VIEW,
        is_enabled=True,
    ).exists()

    response = api_client.patch(
        f"/api/v1/admin/staff/{staff.id}/permissions/",
        {
            "permissions": [
                {"code": StaffPermissionCode.ORDERS_VIEW, "is_enabled": False},
                {"code": StaffPermissionCode.PRODUCTS_CREATE, "is_enabled": True},
            ]
        },
        format="json",
    )

    assert response.status_code == 200
    assert (
        StaffPermission.objects.get(
            user=staff,
            permission_code=StaffPermissionCode.ORDERS_VIEW,
        ).is_enabled
        is False
    )
    assert (
        StaffPermission.objects.get(
            user=staff,
            permission_code=StaffPermissionCode.PRODUCTS_CREATE,
        ).is_enabled
        is True
    )
