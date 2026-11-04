"""The only custom allauth code (docs/users.md §3).

- No public sign-up, by form or by Google.
- Google signs in an EXISTING, active user whose email matches the Google account's verified
  email. Any other Google account is refused with a clear message, not allauth's generic
  "sign-up closed" page.
"""

from typing import NoReturn

from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect

from apps.users.services.user_service import UserService

NOT_LINKED_MESSAGE = (
    "That Google account isn't linked to a staff account on this website. Sign in with your "
    "email and password, or ask an administrator to add you."
)


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return False  # admins onboard every user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest, sociallogin) -> bool:
        return False  # Google may sign existing users in, never create new ones

    def pre_social_login(self, request: HttpRequest, sociallogin) -> None:
        """Runs after Google answers, before allauth logs anyone in."""
        if sociallogin.is_existing:
            if sociallogin.user is None or not sociallogin.user.is_active:
                self._refuse(request)
            return  # this Google account is already connected to an active user

        email = self._verified_email(sociallogin)
        user = UserService().active_user_for_email(email) if email else None
        if user is None:
            self._refuse(request)
        # First Google sign-in for this staff member: connect the account, then allauth logs
        # them in as that user.
        sociallogin.connect(request, user)

    @staticmethod
    def _verified_email(sociallogin) -> str | None:
        for address in sociallogin.email_addresses:
            if address.verified and address.email:
                return address.email
        return None

    @staticmethod
    def _refuse(request: HttpRequest) -> NoReturn:
        messages.error(request, NOT_LINKED_MESSAGE)
        raise ImmediateHttpResponse(redirect("account_login"))
