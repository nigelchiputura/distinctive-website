"""Onboarding and managing staff users (docs/users.md §2, §7).

The admin's "Add user" screen and `manage.py onboard_user` both end in the same place: an active
staff user with no password, in the Content Editor group, who receives a link to set one.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass

from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from apps.core.exceptions import ValidationError
from apps.core.services.base import BaseService
from apps.users.models import User
from apps.users.permissions import CONTENT_EDITOR, codenames
from apps.users.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

Mailer = Callable[..., int]
TokenMaker = Callable[[User], str]

WELCOME_SUBJECT = "Your Distinctive website account"
WELCOME_BODY = """Hello {name},

An account has been created for you to manage the Distinctive Consultancy Services website.

Set your password here (the link works once, for {days} days):
{link}

Then sign in at {login_url} with this email address, {email}.{google_line}

If you weren't expecting this, you can ignore this email.
"""


@dataclass(frozen=True)
class OnboardResult:
    user: User
    set_password_link: str
    email_sent: bool


class UserService(BaseService):
    def __init__(
        self,
        repo: UserRepository | None = None,
        mailer: Mailer | None = None,
        make_token: TokenMaker | None = None,
    ):
        self.repo = repo or UserRepository()
        self.mailer = mailer or send_mail
        # allauth's reset token (it reads the user's email records, so it needs the database).
        self.make_token = make_token or default_token_generator.make_token

    # ---- onboarding ------------------------------------------------------------------------

    def onboard_user(
        self,
        email: str,
        first_name: str = "",
        last_name: str = "",
        group: str = CONTENT_EDITOR,
        send_email: bool = True,
    ) -> OnboardResult:
        email = (email or "").strip().lower()
        if "@" not in email:
            raise ValidationError(errors={"email": ["Enter a valid email address."]})
        if self.repo.get_by_email(email) is not None:
            raise ValidationError(errors={"email": [f"{email} already has an account."]})

        user = self.repo.create_user(
            email, first_name=first_name.strip(), last_name=last_name.strip(), is_staff=True
        )  # no password: unusable until they set one
        if group:
            self.repo.add_to_group(user, group)

        return self.welcome(user, send_email=send_email)

    def welcome(self, user: User, send_email: bool = True) -> OnboardResult:
        """Make a set-password link for a new user and (normally) email it to them. Used by
        onboard_user and by the admin's "Add user" screen."""
        link = self.set_password_link(user)
        sent = self._send_welcome(user, link) if send_email else False
        return OnboardResult(user=user, set_password_link=link, email_sent=sent)

    def set_password_link(self, user: User) -> str:
        """A one-time link to allauth's set-password page, valid for PASSWORD_RESET_TIMEOUT."""
        path = reverse(
            "account_reset_password_from_key",
            kwargs={
                "uidb36": user_pk_to_url_str(user),
                "key": self.make_token(user),
            },
        )
        return settings.SITE_URL.rstrip("/") + path

    def _send_welcome(self, user: User, link: str) -> bool:
        body = WELCOME_BODY.format(
            name=user.first_name or user.email,
            days=round(settings.PASSWORD_RESET_TIMEOUT / 86400),
            link=link,
            login_url=settings.SITE_URL.rstrip("/") + reverse("account_login"),
            email=user.email,
            google_line=(
                " You can also use the Google account with that address."
                if settings.GOOGLE_LOGIN_ENABLED
                else ""
            ),
        )
        try:
            self.mailer(
                WELCOME_SUBJECT,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as exc:  # the account exists either way; the link can be sent by hand
            logger.warning("Welcome email to user %s failed: %s", user.pk, exc)
            return False
        return True

    # ---- lookups and changes ---------------------------------------------------------------

    def active_user_for_email(self, email: str) -> User | None:
        """The active user with this email, for Google sign-in; None if none or inactive."""
        user = self.repo.get_by_email(email)
        return user if user is not None and user.is_active else None

    def deactivate(self, user: User) -> User:
        """Leavers are deactivated, never deleted, so their history in the admin stays."""
        return self.repo.set_active(user, False)

    # ---- the Content Editor group ----------------------------------------------------------

    def sync_content_editor_group(self) -> list[str]:
        """Give the group exactly its permissions (apps/users/permissions.py). Idempotent."""
        return self.repo.set_group_permissions(CONTENT_EDITOR, codenames())
