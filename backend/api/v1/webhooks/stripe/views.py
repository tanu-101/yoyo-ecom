from __future__ import annotations

import stripe
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.payments.services.stripe_webhooks import construct_stripe_event, process_stripe_event

from .serializers import StripeWebhookSerializer


@extend_schema(request=StripeWebhookSerializer, responses=dict)
@api_view(["POST"])
@permission_classes([AllowAny])
def stripe_webhook(request: Request) -> Response:
    endpoint_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    if endpoint_secret:
        try:
            construct_stripe_event(request.body, sig_header, endpoint_secret)
        except (ValueError, stripe.error.SignatureVerificationError):  # type: ignore[attr-defined]
            return Response(
                {"error": {"code": "stripe_signature_invalid", "message": "Invalid signature."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

    serializer = StripeWebhookSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                "error": {
                    "code": "validation_error",
                    "message": "Invalid payload.",
                    "fields": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = process_stripe_event(
        event_id=serializer.validated_data["id"],
        event_type=serializer.validated_data["type"],
        payload=serializer.validated_data,
    )

    if result.get("error"):
        return Response(
            {"error": {"code": "webhook_error", "message": result["error"]}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({"data": result, "message": "Webhook processed."})
