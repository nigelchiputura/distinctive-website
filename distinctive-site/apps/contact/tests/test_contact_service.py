"""ContactService with a fake repository and a fake mailer: no database (Test_Plan §3.3)."""

import logging

import pytest
from django.test import override_settings

from apps.contact.models import ContactSubmission
from apps.contact.services.contact_service import ContactService

ENQUIRY = {
    "name": "Tendai Moyo",
    "email": "tendai@example.org",
    "phone": "+263 77 000 0000",
    "message": "Please call me about an HR audit.",
}


class FakeRepo:
    def __init__(self, log):
        self.log = log

    def create(self, **data):
        self.log.append("saved")
        return ContactSubmission(pk=7, **data)

    def mark_emailed(self, submission):
        self.log.append("marked emailed")
        submission.email_sent, submission.email_error = True, ""
        return submission

    def record_email_error(self, submission, error):
        self.log.append("error recorded")
        submission.email_sent, submission.email_error = False, error
        return submission

    def mark_handled(self, submissions):
        return len(submissions)


class FakeMailer:
    def __init__(self, log, fail_with=None):
        self.log, self.fail_with, self.sent = log, fail_with, []

    def __call__(self, message):
        self.log.append("send attempted")
        if self.fail_with:
            raise self.fail_with
        self.sent.append(message)


def service(fail_with=None):
    log: list[str] = []
    mailer = FakeMailer(log, fail_with)
    return ContactService(FakeRepo(log), mailer), mailer, log


def test_saved_before_the_email_is_attempted_and_marked_sent():
    svc, _, log = service()
    submission = svc.submit(ENQUIRY)
    assert log == ["saved", "send attempted", "marked emailed"]
    assert submission.email_sent is True


def test_a_failed_send_is_recorded_logged_and_never_raised(caplog):
    svc, _, log = service(fail_with=RuntimeError("Resend said: domain not verified"))
    with caplog.at_level(logging.WARNING, logger="apps.contact"):
        submission = svc.submit(ENQUIRY)
    assert log == ["saved", "send attempted", "error recorded"]
    assert submission.email_sent is False
    assert submission.email_error == "RuntimeError: Resend said: domain not verified"
    assert "saved but not emailed" in caplog.text and "domain not verified" in caplog.text


@override_settings(
    CONTACT_RECIPIENT="enquiries@distinctive.co.zw",
    DEFAULT_FROM_EMAIL="Distinctive Website <website@mail.distinctive.co.zw>",
)
def test_recipient_reply_to_and_subject():
    svc, mailer, _ = service()
    svc.submit(ENQUIRY, source_page="services")
    (message,) = mailer.sent
    assert message.to == ["enquiries@distinctive.co.zw"]
    assert message.reply_to == ["tendai@example.org"]
    assert message.from_email == "Distinctive Website <website@mail.distinctive.co.zw>"
    assert message.subject == "Website enquiry from Tendai Moyo (Services page)"
    assert "Please call me about an HR audit." in message.body
    assert "+263 77 000 0000" in message.body


def test_html_in_the_message_is_sent_as_plain_text():
    svc, mailer, _ = service()
    svc.submit({**ENQUIRY, "message": "<b>Hi</b><script>x()</script>"})
    (message,) = mailer.sent
    assert message.content_subtype == "plain" and not getattr(message, "alternatives", [])
    assert "<b>Hi</b><script>x()</script>" in message.body  # as typed, never rendered


def test_a_name_cannot_add_lines_to_the_subject():
    svc, mailer, _ = service()
    submission = svc.submit({**ENQUIRY, "name": "Eve\r\nBcc: someone@example.org"})
    assert submission.name == "Eve Bcc: someone@example.org"
    assert "\n" not in mailer.sent[0].subject


def test_resend_sends_again_and_updates_the_flags():
    svc, mailer, log = service(fail_with=RuntimeError("down"))
    submission = svc.submit(ENQUIRY)
    assert submission.email_sent is False
    mailer.fail_with = None
    log.clear()
    assert svc.resend(submission).email_sent is True
    assert log == ["send attempted", "marked emailed"]


def test_the_ip_is_stored_only_as_a_keyed_hash():
    svc, _, _ = service()
    submission = svc.submit(ENQUIRY, ip="197.221.0.10", user_agent="x" * 400)
    assert submission.ip_hash and "197.221" not in submission.ip_hash
    assert len(submission.ip_hash) == 64
    assert submission.ip_hash == ContactService.hash_ip("197.221.0.10")
    assert ContactService.hash_ip("") == ""
    assert len(submission.user_agent) == 300


def test_mark_handled_goes_through_the_repository():
    svc, _, _ = service()
    assert svc.mark_handled([ContactSubmission(), ContactSubmission()]) == 2


@pytest.mark.parametrize("phone", ["", None])
def test_phone_is_optional(phone):
    svc, mailer, _ = service()
    data = {k: v for k, v in ENQUIRY.items() if k != "phone"}
    if phone is not None:
        data["phone"] = phone
    assert svc.submit(data).phone == ""
    assert "Phone:   -" in mailer.sent[0].body
