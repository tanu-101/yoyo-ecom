from __future__ import annotations

from django.db import transaction

from apps.accounts.models import User, UserOTP
from apps.accounts.selectors.users import get_valid_otp
from apps.accounts.services.authentication import create_otp
from apps.common.exceptions import BusinessRuleViolation
from apps.notifications.services.sms import send_sms

OTP_EXPIRY_MINUTES = 10


@transaction.atomic
def request_phone_verification(*, user: User) -> None:
    if user.is_phone_verified:
        raise BusinessRuleViolation("Phone is already verified.", code="phone_already_verified")

    if not user.phone:
        raise BusinessRuleViolation("No phone number on file.", code="no_phone")

    _, code = create_otp(user=user, purpose=UserOTP.Purpose.PHONE_VERIFICATION)

    success = send_sms(
        to=user.phone,
        body=f"Your verification code is {code}. It expires in {OTP_EXPIRY_MINUTES} minutes.",
    )
    if not success:
        raise BusinessRuleViolation("Failed to send SMS.", code="sms_send_failed")


@transaction.atomic
def verify_phone(*, user: User, code: str) -> None:
    otp = get_valid_otp(
        user=user,
        purpose=UserOTP.Purpose.PHONE_VERIFICATION,
        code_hash=_hash_code(code),
    )
    if otp is None:
        raise BusinessRuleViolation("Invalid or expired verification code.", code="invalid_otp")
    otp.consume()
    user.is_phone_verified = True
    user.save(update_fields=["is_phone_verified"])


@transaction.atomic
def request_phone_change(*, user: User, new_phone: str) -> None:
    if not new_phone:
        raise BusinessRuleViolation("New phone number is required.", code="phone_required")

    _, code = create_otp(user=user, purpose=UserOTP.Purpose.PHONE_CHANGE)

    success = send_sms(
        to=new_phone,
        body=f"Your phone change code is {code}. It expires in {OTP_EXPIRY_MINUTES} minutes.",
    )
    if not success:
        raise BusinessRuleViolation("Failed to send SMS.", code="sms_send_failed")


@transaction.atomic
def confirm_phone_change(*, user: User, code: str, new_phone: str) -> None:
    otp = get_valid_otp(
        user=user,
        purpose=UserOTP.Purpose.PHONE_CHANGE,
        code_hash=_hash_code(code),
    )
    if otp is None:
        raise BusinessRuleViolation("Invalid or expired verification code.", code="invalid_otp")
    otp.consume()
    user.phone = new_phone
    user.is_phone_verified = True
    user.save(update_fields=["phone", "is_phone_verified"])


def _hash_code(code: str) -> str:
    import hashlib

    return hashlib.sha256(code.encode("utf-8")).hexdigest()
