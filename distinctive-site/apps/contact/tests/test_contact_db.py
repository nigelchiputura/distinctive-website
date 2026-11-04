"""The repository and the admin, against the real database."""

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.test import override_settings

from apps.contact.models import ContactSubmission
from apps.contact.repositories.contact_repository import ContactRepository
from apps.contact.services.contact_service import ContactService
from apps.users.permissions import CONTENT_EDITOR

pytestmark = pytest.mark.django_db
ADMIN = f"/{settings.ADMIN_URL_PATH}contact/contactsubmission/"


def enquiry(**extra):
    data = {"name": "Rudo", "email": "rudo@example.org", "message": "Hello", **extra}
    return ContactSubmission.objects.create(**data)


def test_repository_flags():
    repo = ContactRepository()
    s = enquiry()
    repo.record_email_error(s, "boom")
    s.refresh_from_db()
    assert (s.email_sent, s.email_error) == (False, "boom")
    repo.mark_emailed(s)
    s.refresh_from_db()
    assert s.email_sent and s.emailed_at and s.email_error == ""
    assert repo.mark_handled([s]) == 1
    assert repo.mark_handled([s]) == 0  # already handled
    s.refresh_from_db()
    assert s.handled and s.handled_at


def test_submit_through_the_real_backend_saves_and_sends():
    submission = ContactService().submit(
        {"name": "Rudo Moyo", "email": "rudo@example.org", "message": "Hello"}
    )
    submission.refresh_from_db()
    assert submission.email_sent is True
    assert len(mail.outbox) == 1 and mail.outbox[0].reply_to == ["rudo@example.org"]


@pytest.fixture
def editor_client(client):
    user = get_user_model().objects.create_user("editor@distinctive.co.zw", "A-long-password-2026")
    user.is_staff = True
    user.save()
    user.groups.add(Group.objects.get(name=CONTENT_EDITOR))
    client.force_login(user)
    return client


def test_editor_reads_enquiries_but_cannot_add_or_delete(editor_client):
    s = enquiry()
    assert editor_client.get(ADMIN).status_code == 200
    page = editor_client.get(f"{ADMIN}{s.pk}/change/")
    assert page.status_code == 200 and b"rudo@example.org" in page.content
    assert editor_client.get(f"{ADMIN}add/").status_code == 403
    assert editor_client.get(f"{ADMIN}{s.pk}/delete/").status_code == 403


def test_mark_handled_action(editor_client):
    s = enquiry()
    editor_client.post(ADMIN, {"action": "mark_handled", "_selected_action": [s.pk]})
    s.refresh_from_db()
    assert s.handled


def test_resend_action_sends_an_unsent_enquiry(editor_client):
    s = enquiry(email_error="RuntimeError: down")
    response = editor_client.post(
        ADMIN, {"action": "resend_notification", "_selected_action": [s.pk]}, follow=True
    )
    s.refresh_from_db()
    assert s.email_sent and s.email_error == ""
    assert len(mail.outbox) == 1
    assert b"Sent 1 notification email" in response.content


@override_settings(EMAIL_BACKEND="apps.contact.tests.failing_backend.EmailBackend")
def test_resend_action_reports_a_failure(editor_client):
    s = enquiry()
    response = editor_client.post(
        ADMIN, {"action": "resend_notification", "_selected_action": [s.pk]}, follow=True
    )
    s.refresh_from_db()
    assert not s.email_sent and "provider unavailable" in s.email_error
    assert b"still couldn" in response.content
