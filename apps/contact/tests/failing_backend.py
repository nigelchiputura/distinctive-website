"""An email backend that always fails, standing in for a provider outage in tests."""

from django.core.mail.backends.base import BaseEmailBackend


class EmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise ConnectionError("provider unavailable")
