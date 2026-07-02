from __future__ import annotations

import stripe
from django.db import transaction
from django.utils import timezone

from apps.payments.constants import PaymentProvider
from apps.payments.models import Payment, PaymentEvent
from apps.payments.services.stripe_payment_intents import (
    confirm_payment_failure,
    confirm_payment_success,
)


def construct_stripe_event(payload: bytes, sig_header: str, endpoint_secret: str) -> stripe.Event:
    return stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)


def _get_payment_by_intent(intent_id: str) -> Payment | None:
    return Payment.objects.filter(provider_payment_intent_id=intent_id).first()


@transaction.atomic
def process_stripe_event(*, event_id: str, event_type: str, payload: dict) -> dict:
    existing = PaymentEvent.objects.filter(event_id=event_id).first()
    if existing:
        if existing.processed_at:
            return {"status": "duplicate", "message": "Event already processed."}
        existing.processed_at = timezone.now()
        existing.save(update_fields=["processed_at"])
        return {"status": "reprocessed", "message": "Event reprocessed."}

    event = PaymentEvent.objects.create(
        provider=PaymentProvider.STRIPE,
        event_id=event_id,
        event_type=event_type,
        payload=payload,
    )

    result = {"status": "processed", "event_id": str(event.id)}

    try:
        data_object = payload.get("data", {}).get("object", {})

        if event_type == "payment_intent.succeeded":
            intent_id = data_object.get("id", "")
            payment = _get_payment_by_intent(intent_id=intent_id)
            if payment:
                charge_id = ""
                charges = data_object.get("charges", {})
                if isinstance(charges, dict):
                    charge_list = charges.get("data", [])
                    if charge_list:
                        charge_id = charge_list[0].get("id", "")
                confirm_payment_success(payment=payment, provider_payment_intent_id=intent_id)
                if charge_id:
                    payment.provider_charge_id = charge_id
                    payment.save(update_fields=["provider_charge_id"])
                result["payment_id"] = str(payment.id)
            else:
                event.processing_error = f"No payment found for intent {intent_id}"
                event.save(update_fields=["processing_error"])

        elif event_type == "payment_intent.payment_failed":
            intent_id = data_object.get("id", "")
            last_error = data_object.get("last_payment_error", {})
            failure_reason = last_error.get("message", "Unknown error")
            payment = _get_payment_by_intent(intent_id=intent_id)
            if payment:
                confirm_payment_failure(payment=payment, failure_reason=failure_reason)

        elif event_type == "charge.refunded":
            charge_id = data_object.get("id", "")
            payment = Payment.objects.filter(provider_charge_id=charge_id).first()
            if payment:
                refunded_amount = data_object.get("amount_refunded", 0)
                result["payment_id"] = str(payment.id)
                result["refunded_amount"] = refunded_amount

    except Exception as exc:
        event.processing_error = str(exc)
        event.save(update_fields=["processing_error"])
        event.refresh_from_db()
        result["error"] = str(exc)

    event.processed_at = timezone.now()
    event.save(update_fields=["processed_at"])

    return result
