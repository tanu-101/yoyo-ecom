from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, UserOTP
from apps.accounts.selectors.users import get_active_user_by_email, get_valid_otp
from apps.common.exceptions import BusinessRuleViolation

OTP_EXPIRY_MINUTES = 10


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def issue_tokens(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@transaction.atomic
def register_customer(
    *,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    phone: str = "",
) -> User:
    from apps.accounts.services.users import create_user

    return create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role="customer",
    )


def authenticate_user(*, email: str, password: str) -> User:
    user = authenticate(username=email, password=password)
    if not user or not user.is_active or user.deleted_at is not None:
        raise BusinessRuleViolation("Invalid credentials.", code="auth_invalid_credentials")
    return user


def logout_refresh_token(refresh_token: str) -> None:
    try:
        token = RefreshToken(refresh_token)  # type: ignore[arg-type]
        token.blacklist()
    except Exception as exc:
        raise BusinessRuleViolation("Invalid refresh token.", code="auth_invalid_refresh") from exc


@transaction.atomic
def change_password(*, user: User, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise BusinessRuleViolation("Old password is incorrect.", code="invalid_old_password")
    validate_password(new_password, user=user)
    user.set_password(new_password)
    user.save(update_fields=["password"])


@transaction.atomic
def create_otp(*, user: User, purpose: str) -> tuple[UserOTP, str]:
    code = _generate_code()
    otp = UserOTP.objects.create(
        user=user,
        purpose=purpose,
        code_hash=_hash_code(code),
        expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    return otp, code


def request_email_verification(user: User) -> None:
    _, code = create_otp(user=user, purpose=UserOTP.Purpose.EMAIL_VERIFICATION)
    send_mail(
        "Verify your email",
        f"Your verification code is {code}. It expires in {OTP_EXPIRY_MINUTES} minutes.",
        None,
        [user.email],
        fail_silently=False,
    )


@transaction.atomic
def verify_email(*, user: User, code: str) -> None:
    otp = get_valid_otp(
        user=user,
        purpose=UserOTP.Purpose.EMAIL_VERIFICATION,
        code_hash=_hash_code(code),
    )
    if otp is None:
        raise BusinessRuleViolation("Invalid or expired verification code.", code="invalid_otp")
    otp.consume()
    user.is_email_verified = True
    user.save(update_fields=["is_email_verified"])


def request_password_reset(email: str) -> None:
    user = get_active_user_by_email(email)
    if user is None:
        return
    _, code = create_otp(user=user, purpose=UserOTP.Purpose.PASSWORD_RESET)
    send_mail(
        "Reset your password",
        f"Your password reset code is {code}. It expires in {OTP_EXPIRY_MINUTES} minutes.",
        None,
        [user.email],
        fail_silently=False,
    )


@transaction.atomic
def reset_password(*, email: str, code: str, new_password: str) -> None:
    user = get_active_user_by_email(email)
    if user is None:
        raise BusinessRuleViolation("Invalid or expired reset code.", code="invalid_otp")
    otp = get_valid_otp(
        user=user,
        purpose=UserOTP.Purpose.PASSWORD_RESET,
        code_hash=_hash_code(code),
    )
    if otp is None:
        raise BusinessRuleViolation("Invalid or expired reset code.", code="invalid_otp")
    validate_password(new_password, user=user)
    otp.consume()
    user.set_password(new_password)
    user.save(update_fields=["password"])
