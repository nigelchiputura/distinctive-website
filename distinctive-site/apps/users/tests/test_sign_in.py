"""Sign-in, set-password, onboarding and the admin, through the real stack (database)."""

import importlib
import re

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.core.management import CommandError, call_command
from django.test import override_settings
from django.urls import clear_url_caches

from apps.users.permissions import CONTENT_EDITOR

pytestmark = pytest.mark.django_db
User = get_user_model()
PASSWORD = "A-good-long-password-2026"


def test_sign_in_page_is_staff_only_with_no_sign_up_link(client):
    html = client.get("/accounts/login/").content.decode()
    assert "Staff sign in" in html
    assert "/accounts/signup/" not in html
    assert "Sign in with Google" not in html  # no Google credentials configured
    assert "+263 (24) 2 486 642 - 3" in html  # the site's details, not allauth's "site" record


def test_sign_up_is_closed(client):
    assert "Sign Up Closed" in client.get("/accounts/signup/").content.decode()
    client.post(
        "/accounts/signup/",
        {"email": "x@example.org", "password1": PASSWORD, "password2": PASSWORD},
    )
    assert not User.objects.filter(email="x@example.org").exists()


def test_password_sign_in_lands_in_the_admin(client):
    User.objects.create_superuser("owner@distinctive.co.zw", PASSWORD)
    response = client.post(
        "/accounts/login/?next=/admin/", {"login": "OWNER@distinctive.co.zw", "password": PASSWORD}
    )
    assert response.status_code == 302 and response.url == "/admin/"
    assert client.get("/admin/").status_code == 200


def test_wrong_password_is_refused(client):
    User.objects.create_superuser("owner@distinctive.co.zw", PASSWORD)
    response = client.post(
        "/accounts/login/", {"login": "owner@distinctive.co.zw", "password": "nope"}
    )
    assert response.status_code == 200
    assert "not correct" in response.content.decode()


def test_the_admins_own_login_redirects_to_the_one_sign_in_page(client):
    response = client.get("/admin/login/?next=/admin/core/sitesettings/")
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/admin/core/sitesettings/"


def google_settings():
    return override_settings(
        GOOGLE_LOGIN_ENABLED=True,
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "SCOPE": ["profile", "email"],
                "APPS": [{"client_id": "id", "secret": "s", "key": ""}],
            }
        },
    )


def test_google_button_appears_when_configured(client):
    with google_settings():
        html = client.get("/accounts/login/").content.decode()
    assert "Sign in with Google" in html
    assert 'action="/accounts/google/login/' in html and 'method="post"' in html


def test_google_sign_in_starts_with_a_post_to_google(client):
    with google_settings():
        response = client.post("/accounts/google/login/")
    assert response.status_code == 302
    assert response.url.startswith("https://accounts.google.com/o/oauth2/")


def link_path(text: str) -> str:
    return re.search(r"https?://[^/\s]+(/accounts/password/reset/key/\S+)", text).group(1)


def test_onboard_command_and_setting_a_password(client):
    call_command("onboard_user", "Rudo.Moyo@distinctive.co.zw", "--first", "Rudo")
    user = User.objects.get(email="rudo.moyo@distinctive.co.zw")
    assert user.is_staff and not user.has_usable_password()
    assert list(user.groups.values_list("name", flat=True)) == [CONTENT_EDITOR]
    (welcome,) = mail.outbox

    # The link leads to the set-password page (allauth redirects once to hide the key).
    page = client.get(link_path(welcome.body), follow=True)
    assert "Set your password" in page.content.decode()
    done = client.post(
        page.redirect_chain[-1][0], {"password1": PASSWORD, "password2": PASSWORD}, follow=True
    )
    assert "Password set" in done.content.decode()
    assert client.login(username="rudo.moyo@distinctive.co.zw", password=PASSWORD)

    # The link works once.
    again = client.get(link_path(welcome.body), follow=True)
    assert "This link has expired" in again.content.decode()


def test_onboard_command_without_email_prints_the_link(capsys):
    call_command("onboard_user", "a@distinctive.co.zw", "--no-email")
    assert "/accounts/password/reset/key/" in capsys.readouterr().out
    assert mail.outbox == []


def test_onboard_command_refuses_a_duplicate():
    call_command("onboard_user", "a@distinctive.co.zw", "--no-email")
    with pytest.raises(CommandError, match="already has an account"):
        call_command("onboard_user", "A@distinctive.co.zw", "--no-email")


def test_admin_add_user_onboards_them(admin_client):
    editor = Group.objects.get(name=CONTENT_EDITOR)
    page = admin_client.get("/admin/users/user/add/").content.decode()
    assert 'name="password1"' not in page  # no password to type: they set their own
    response = admin_client.post(
        "/admin/users/user/add/",
        {
            "email": "Tsitsi@Distinctive.co.zw",
            "first_name": "Tsitsi",
            "last_name": "N",
            "groups": [editor.pk],
            "_save": "Save",
        },
    )
    assert response.status_code == 302, response.content.decode()[:2000]
    user = User.objects.get(email="tsitsi@distinctive.co.zw")
    assert user.is_staff and not user.has_usable_password() and user.username == "tsitsi"
    assert list(user.groups.all()) == [editor]
    assert len(mail.outbox) == 1 and mail.outbox[0].to == ["tsitsi@distinctive.co.zw"]


def test_admin_deactivate_action_never_deactivates_yourself(admin_client, admin_user):
    other = User.objects.create_user("b@distinctive.co.zw", PASSWORD, is_staff=True)
    admin_client.post(
        "/admin/users/user/",
        {"action": "deactivate_users", "_selected_action": [other.pk, admin_user.pk]},
    )
    other.refresh_from_db()
    admin_user.refresh_from_db()
    assert (other.is_active, admin_user.is_active) == (False, True)


def test_content_editor_permissions(client):
    editor = User.objects.create_user("editor@distinctive.co.zw", PASSWORD, is_staff=True)
    editor.groups.add(Group.objects.get(name=CONTENT_EDITOR))
    client.force_login(editor)
    assert client.get("/admin/core/sitesettings/1/change/").status_code == 200
    assert client.get("/admin/users/user/").status_code == 403
    assert client.get("/admin/auth/group/").status_code == 403
    perms = set(
        Group.objects.get(name=CONTENT_EDITOR).permissions.values_list("codename", flat=True)
    )
    assert {"change_sitesettings", "view_sitesettings"} <= perms
    assert not any("user" in p or "group" in p or "permission" in p for p in perms)


def test_admin_path_comes_from_the_setting(client, admin_user):
    import config.urls

    try:
        with override_settings(ADMIN_URL_PATH="staff-area-7f3/"):
            clear_url_caches()
            importlib.reload(config.urls)
            client.force_login(admin_user)
            assert client.get("/staff-area-7f3/").status_code == 200
            assert client.get("/admin/").status_code == 404
    finally:
        clear_url_caches()
        importlib.reload(config.urls)
