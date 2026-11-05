"""UserService with a fake repository and a fake mailer: no database."""

import pytest
from django.test import override_settings

from apps.core.exceptions import ValidationError
from apps.users.models import User
from apps.users.permissions import CONTENT_EDITOR, codenames
from apps.users.services.user_service import UserService


class FakeRepo:
    def __init__(self, existing=()):
        self.users = {u.email: u for u in existing}
        self.groups: dict[str, list[str]] = {}
        self.granted = None

    def get_by_email(self, email):
        return self.users.get(email.strip().lower())

    def create_user(self, email, **fields):
        user = User(pk=len(self.users) + 1, email=email, username=email.split("@")[0], **fields)
        user.set_unusable_password()
        self.users[email] = user
        return user

    def add_to_group(self, user, name):
        self.groups.setdefault(name, []).append(user.email)

    def set_active(self, user, active):
        user.is_active = active
        return user

    def set_group_permissions(self, name, pairs):
        self.granted = (name, pairs)
        return [f"{a}.{c}" for a, c in pairs]


class FakeMailer:
    def __init__(self, fail=False):
        self.sent = []
        self.fail = fail

    def __call__(self, subject, body, sender, recipients, fail_silently=False):
        if self.fail:
            raise ConnectionError("Resend unreachable")
        self.sent.append((subject, body, sender, recipients))
        return 1


def make_service(repo, mailer):
    return UserService(repo, mailer, make_token=lambda user: "tok-en123")


@override_settings(SITE_URL="https://new.distinctive.co.zw")
def test_onboard_creates_a_staff_user_with_no_password_and_emails_a_link():
    repo, mailer = FakeRepo(), FakeMailer()
    result = make_service(repo, mailer).onboard_user(
        "  Rudo.Moyo@Distinctive.co.zw ", "Rudo", "Moyo"
    )

    user = result.user
    assert (user.email, user.first_name, user.is_staff) == (
        "rudo.moyo@distinctive.co.zw",
        "Rudo",
        True,
    )
    assert not user.has_usable_password()
    assert repo.groups == {CONTENT_EDITOR: ["rudo.moyo@distinctive.co.zw"]}
    assert result.email_sent
    assert result.set_password_link == (
        f"https://new.distinctive.co.zw/accounts/password/reset/key/{user.pk}-tok-en123/"
    )
    ((subject, body, _sender, recipients),) = mailer.sent
    assert recipients == ["rudo.moyo@distinctive.co.zw"]
    assert result.set_password_link in body and "Hello Rudo" in body


@pytest.mark.parametrize("email", ["", "not-an-email", "   "])
def test_onboard_refuses_a_bad_email(email):
    with pytest.raises(ValidationError) as caught:
        make_service(FakeRepo(), FakeMailer()).onboard_user(email)
    assert "email" in caught.value.errors


def test_onboard_refuses_an_existing_email_whatever_its_case():
    taken = User(pk=1, email="rudo@distinctive.co.zw")
    with pytest.raises(ValidationError, match=r"(?s).*") as caught:
        make_service(FakeRepo([taken]), FakeMailer()).onboard_user("RUDO@distinctive.co.zw")
    assert caught.value.errors["email"] == ["rudo@distinctive.co.zw already has an account."]


def test_a_failed_email_still_creates_the_user_and_returns_the_link(caplog):
    result = make_service(FakeRepo(), FakeMailer(fail=True)).onboard_user("a@distinctive.co.zw")
    assert result.user.email == "a@distinctive.co.zw"
    assert result.email_sent is False
    assert "/accounts/password/reset/key/" in result.set_password_link
    assert "Welcome email" in caplog.text


def test_no_email_when_asked_not_to():
    mailer = FakeMailer()
    result = make_service(FakeRepo(), mailer).onboard_user("a@distinctive.co.zw", send_email=False)
    assert result.email_sent is False and mailer.sent == []


def test_no_group_when_none_given():
    repo = FakeRepo()
    make_service(repo, FakeMailer()).onboard_user("a@distinctive.co.zw", group="")
    assert repo.groups == {}


@override_settings(GOOGLE_LOGIN_ENABLED=True)
def test_welcome_mentions_google_when_it_is_enabled():
    mailer = FakeMailer()
    make_service(FakeRepo(), mailer).onboard_user("a@distinctive.co.zw")
    assert "Google account" in mailer.sent[0][1]


def test_active_user_for_email():
    active = User(pk=1, email="a@distinctive.co.zw", is_active=True)
    gone = User(pk=2, email="b@distinctive.co.zw", is_active=False)
    service = make_service(FakeRepo([active, gone]), FakeMailer())
    assert service.active_user_for_email("A@distinctive.co.zw") is active
    assert service.active_user_for_email("b@distinctive.co.zw") is None
    assert service.active_user_for_email("c@distinctive.co.zw") is None


def test_deactivate():
    user = User(pk=1, email="a@distinctive.co.zw", is_active=True)
    assert make_service(FakeRepo([user]), FakeMailer()).deactivate(user).is_active is False


def test_sync_content_editor_group_asks_for_exactly_the_listed_permissions():
    repo = FakeRepo()
    UserService(repo, FakeMailer()).sync_content_editor_group()
    name, pairs = repo.granted
    assert name == CONTENT_EDITOR and pairs == codenames()
    assert not any(app in ("users", "auth", "account", "socialaccount") for app, _ in pairs)
