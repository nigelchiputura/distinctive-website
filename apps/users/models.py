"""The custom user. Created on Phase 1 Day 1, before any other migration (docs/users.md §1)."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A staff member who manages the website. The public site has no accounts.

    Login is by email. ``username`` is kept because AbstractUser requires it; Day 4's
    UserService fills it from the email, so admins only type an email.
    """

    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["email"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def save(self, *args, **kwargs):
        # One account per address, whatever the capitalisation.
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email
