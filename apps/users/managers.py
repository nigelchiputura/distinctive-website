"""User manager for email login: the username is filled in from the email (docs/users.md §1).

AbstractUser still has a unique `username` column. Admins only ever type an email, so the manager
makes a username from the email's local part ("tendai.m" from tendai.m@distinctive.co.zw), adding
a number if it's taken. This lives on the model's manager, not in a service, because Django's own
machinery (createsuperuser, the admin, test fixtures) calls create_user/create_superuser directly.
"""

from typing import Any

from django.contrib.auth.models import UserManager as DjangoUserManager
from django.utils.text import slugify


class UserManager(DjangoUserManager):
    @staticmethod
    def username_for(model, email: str) -> str:
        """A unique username from the email's local part: tendai.m, then tendai.m2, …"""
        local = email.split("@", 1)[0]
        base = (slugify(local.replace(".", "-")).replace("-", ".") or "user")[:140]
        candidate, n = base, 2
        while model._default_manager.filter(username=candidate).exists():
            candidate, n = f"{base}{n}", n + 1
        return candidate

    def _username_from(self, email: str) -> str:
        return self.username_for(self.model, email)

    def create_user(  # type: ignore[override]
        self, email: str, password: str | None = None, **extra_fields: Any
    ):
        email = self.normalize_email(email).strip().lower()
        username = extra_fields.pop("username", None) or self._username_from(email)
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(  # type: ignore[override]
        self, email: str, password: str | None = None, **extra_fields: Any
    ):
        email = self.normalize_email(email).strip().lower()
        username = extra_fields.pop("username", None) or self._username_from(email)
        return super().create_superuser(username, email, password, **extra_fields)
