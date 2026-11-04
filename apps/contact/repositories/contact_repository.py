"""Queries for enquiries."""

from collections.abc import Iterable

from django.utils import timezone

from apps.contact.models import ContactSubmission
from apps.core.repositories.base import BaseRepository


class ContactRepository(BaseRepository[ContactSubmission]):
    model = ContactSubmission

    def mark_emailed(self, submission: ContactSubmission) -> ContactSubmission:
        return self.update(submission, email_sent=True, emailed_at=timezone.now(), email_error="")

    def record_email_error(self, submission: ContactSubmission, error: str) -> ContactSubmission:
        return self.update(submission, email_sent=False, email_error=error)

    def mark_handled(self, submissions: Iterable[ContactSubmission]) -> int:
        ids = [s.pk for s in submissions]
        return (
            self._manager()
            .filter(pk__in=ids, handled=False)
            .update(handled=True, handled_at=timezone.now())
        )
