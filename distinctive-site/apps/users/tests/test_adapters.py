"""The allauth adapters: no sign-up, and Google only for existing active users."""

from types import SimpleNamespace

import pytest
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from apps.users.adapters import NOT_LINKED_MESSAGE, AccountAdapter, SocialAccountAdapter

pytestmark = pytest.mark.django_db


def request():
    req = RequestFactory().get("/accounts/google/login/callback/")
    SessionMiddleware(lambda r: None).process_request(req)
    req._messages = FallbackStorage(req)
    return req


class FakeSocialLogin:
    def __init__(self, emails=(), existing=False, user=None):
        self.email_addresses = [SimpleNamespace(email=e, verified=v) for e, v in emails]
        self.is_existing = existing
        self.user = user
        self.connected_to = None

    def connect(self, request, user):
        self.connected_to = user


def staff(email="tendai@distinctive.co.zw", active=True):
    return get_user_model().objects.create_user(email, "x" * 12, is_staff=True, is_active=active)


def test_no_sign_up_by_form_or_google():
    assert AccountAdapter().is_open_for_signup(request()) is False
    assert SocialAccountAdapter().is_open_for_signup(request(), FakeSocialLogin()) is False


def test_existing_active_user_is_connected_on_first_google_sign_in():
    user = staff()
    login = FakeSocialLogin(emails=[("Tendai@Distinctive.co.zw", True)])
    SocialAccountAdapter().pre_social_login(request(), login)
    assert login.connected_to == user


@pytest.mark.parametrize(
    ("emails", "active"),
    [
        ([("stranger@gmail.com", True)], True),  # no account with this email
        ([("tendai@distinctive.co.zw", False)], True),  # Google hasn't verified the email
        ([("tendai@distinctive.co.zw", True)], False),  # the account is deactivated
        ([], True),  # no email from Google at all
    ],
)
def test_other_google_accounts_are_refused_politely(emails, active):
    staff(active=active)
    req = request()
    login = FakeSocialLogin(emails=emails)
    with pytest.raises(ImmediateHttpResponse) as caught:
        SocialAccountAdapter().pre_social_login(req, login)
    assert caught.value.response.url == "/accounts/login/"
    assert [str(m) for m in req._messages] == [NOT_LINKED_MESSAGE]
    assert login.connected_to is None


def test_already_connected_google_account_signs_in_unless_deactivated():
    active = FakeSocialLogin(existing=True, user=staff())
    SocialAccountAdapter().pre_social_login(request(), active)  # no exception

    gone = FakeSocialLogin(existing=True, user=staff("left@distinctive.co.zw", active=False))
    with pytest.raises(ImmediateHttpResponse):
        SocialAccountAdapter().pre_social_login(request(), gone)
