from __future__ import annotations

from unittest.mock import patch

import pytest
from django.conf import settings

from apps.notifications.services.sms import send_sms

pytestmark = pytest.mark.django_db

TWILIO_SETTINGS = {
    "TWILIO_ACCOUNT_SID": "test_sid",
    "TWILIO_AUTH_TOKEN": "test_token",
    "TWILIO_PHONE_NUMBER": "+15005550006",
}


class TestSendSMS:
    def test_sends_sms_successfully(self):
        fake_message = type("FakeMessage", (), {"sid": "SM123"})()
        with (
            patch.multiple(settings, **TWILIO_SETTINGS),
            patch(
                "apps.notifications.services.sms.TwilioClient",
            ) as mock_client,
        ):
            mock_client.return_value.messages.create.return_value = fake_message
            result = send_sms(to="+8801700000000", body="Test message")

        assert result is True
        mock_client.return_value.messages.create.assert_called_once_with(
            body="Test message",
            from_="+15005550006",
            to="+8801700000000",
        )

    def test_returns_false_on_twilio_error(self):
        from twilio.base.exceptions import TwilioRestException

        with (
            patch.multiple(settings, **TWILIO_SETTINGS),
            patch(
                "apps.notifications.services.sms.TwilioClient",
            ) as mock_client,
        ):
            mock_client.return_value.messages.create.side_effect = TwilioRestException(
                status=400,
                uri="/Messages",
                msg="Bad request",
            )
            result = send_sms(to="+8801700000000", body="Test")

        assert result is False

    def test_returns_false_if_no_credentials(self):
        with patch.object(settings, "TWILIO_ACCOUNT_SID", ""):
            result = send_sms(to="+8801700000000", body="Test")
        assert result is False

    def test_returns_false_if_no_recipient(self):
        with patch.multiple(settings, **TWILIO_SETTINGS):
            result = send_sms(to="", body="Test")
        assert result is False
