"""Enquiries: save, then email the enquiries mailbox, never losing one (docs/architecture.md §5).

`submit` saves the enquiry first and only then sends the notification. A failed send is logged
with the provider's message and stored on the enquiry; it is never raised to the visitor, whose
enquiry is safe either way. `resend` (the admin action) tries again.
"""

import hashlib
import hmac
import logging
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.core.mail import EmailMessage

from apps.contact.models import ContactSubmission
from apps.contact.repositories.contact_repository import ContactRepository
from apps.core.services.base import BaseService

logger = logging.getLogger(__name__)

ERROR_LIMIT = 1000  # characters of the provider's message kept on the enquiry


def send_email(message: EmailMessage) -> None:
    message.send(fail_silently=False)


def one_line(text: str) -> str:
    """No line breaks: a name in a subject can't add email headers."""
    return " ".join(str(text).split())


class ContactService(BaseService):
    def __init__(
        self,
        repo: ContactRepository | None = None,
        mailer: Callable[[EmailMessage], None] = send_email,
    ):
        self.repo = repo or ContactRepository()
        self.mailer = mailer

    def submit(
        self,
        data: dict[str, Any],
        source_page: str = ContactSubmission.Source.CONTACT,
        ip: str = "",
        user_agent: str = "",
    ) -> ContactSubmission:
        """Save the enquiry, then try to email it. Returns the saved enquiry."""
        submission = self.repo.create(
            name=one_line(data["name"])[:160],
            email=data["email"].strip(),
            phone=one_line(data.get("phone", ""))[:40],
            message=data["message"].strip(),
            source_page=source_page,
            ip_hash=self.hash_ip(ip),
            user_agent=user_agent[:300],
        )
        return self._notify(submission)

    def resend(self, submission: ContactSubmission) -> ContactSubmission:
        """Send the notification again (the admin's "Resend notification email")."""
        return self._notify(submission)

    def mark_handled(self, submissions: list[ContactSubmission]) -> int:
        return self.repo.mark_handled(submissions)

    # ---- helpers ---------------------------------------------------------------------------

    @staticmethod
    def hash_ip(ip: str) -> str:
        """A keyed hash, so the same visitor can be recognised without storing their address."""
        if not ip:
            return ""
        key = settings.SECRET_KEY.encode()
        return hmac.new(key, ip.encode(), hashlib.sha256).hexdigest()

    def build_email(self, submission: ContactSubmission) -> EmailMessage:
        page = submission.get_source_page_display()
        body = "\n".join(
            [
                f"A new enquiry from the website ({page}).",
                "",
                f"Name:    {submission.name}",
                f"Email:   {submission.email}",
                f"Phone:   {submission.phone or '-'}",
                "",
                "Message:",
                submission.message,
                "",
                "--",
                "Reply to this email to answer the visitor directly.",
            ]
        )
        return EmailMessage(
            subject=f"Website enquiry from {submission.name} ({page})",
            body=body,  # plain text: whatever the visitor typed is never sent as HTML
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_RECIPIENT],
            reply_to=[submission.email],
        )

    def _notify(self, submission: ContactSubmission) -> ContactSubmission:
        try:
            self.mailer(self.build_email(submission))
        except Exception as exc:  # any provider failure: the enquiry is already saved
            error = f"{type(exc).__name__}: {exc}"[:ERROR_LIMIT]
            logger.warning("Enquiry %s saved but not emailed: %s", submission.pk, error)
            return self.repo.record_email_error(submission, error)
        return self.repo.mark_emailed(submission)
