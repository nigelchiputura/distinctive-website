"""The email start-up checks, core.W001–W003 (docs/deployment.md §6)."""

import pytest
from django.test import override_settings

from apps.core.checks import email_settings_check

GOOD = "Distinctive Website <website@mail.distinctive.co.zw>"


def ids(**settings):
    with override_settings(**settings):
        return [m.id for m in email_settings_check()]


def test_console_never_warns():
    assert ids(EMAIL_PROVIDER="console", DEFAULT_FROM_EMAIL="x@localhost") == []


@pytest.mark.parametrize(
    "sender",
    ["", "webmaster@localhost", "Site <website@website.localhost>", "a@example.com",
     "a@mail.example.org", "a@intranet", "a@box.local", "a@x.test"],
)  # fmt: skip
def test_w001_sender_not_on_a_real_domain(sender):
    assert "core.W001" in ids(
        EMAIL_PROVIDER="resend", DEFAULT_FROM_EMAIL=sender, ANYMAIL={"RESEND_API_KEY": "re_x"}
    )


def test_w002_resend_without_a_key():
    assert ids(
        EMAIL_PROVIDER="resend", DEFAULT_FROM_EMAIL=GOOD, ANYMAIL={"RESEND_API_KEY": ""}
    ) == ["core.W002"]


def test_w003_smtp_without_a_login():
    assert ids(
        EMAIL_PROVIDER="smtp", DEFAULT_FROM_EMAIL=GOOD, EMAIL_HOST_USER="", EMAIL_HOST_PASSWORD=""
    ) == ["core.W003"]


def test_a_correct_configuration_is_quiet():
    assert (
        ids(EMAIL_PROVIDER="resend", DEFAULT_FROM_EMAIL=GOOD, ANYMAIL={"RESEND_API_KEY": "re_x"})
        == []
    )
    assert (
        ids(
            EMAIL_PROVIDER="smtp",
            DEFAULT_FROM_EMAIL=GOOD,
            EMAIL_HOST_USER="u",
            EMAIL_HOST_PASSWORD="p",
        )
        == []
    )
