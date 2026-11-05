"""Enquiries from the Contact page and the Services enquiry block (docs/architecture.md §5).

Every enquiry is saved before its notification email is attempted, so a provider failure never
loses one: the row keeps `email_sent=False` and the provider's message, and the admin resends it.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, ClassVar

from django.db import models

from apps.core.models import BaseModel


class ContactSubmission(BaseModel):
    class Source(models.TextChoices):
        CONTACT = "contact", "Contact page"
        SERVICES = "services", "Services page"

    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField()
    source_page = models.CharField(
        "sent from", max_length=20, choices=Source.choices, default=Source.CONTACT
    )
    if TYPE_CHECKING:  # added by Django for a field with choices; declared for the type checker
        get_source_page_display: Callable[[], str]

    email_sent = models.BooleanField("email sent", default=False)
    emailed_at = models.DateTimeField(null=True, blank=True)
    email_error = models.TextField(
        blank=True, help_text="What the email provider said, if the notification failed."
    )
    handled = models.BooleanField(default=False, help_text="Someone has replied or dealt with it.")
    handled_at = models.DateTimeField(null=True, blank=True)

    # A keyed hash of the visitor's IP address (rate limiting and abuse checks), never the IP.
    ip_hash = models.CharField(max_length=64, blank=True, editable=False)
    user_agent = models.CharField(max_length=300, blank=True, editable=False)

    class Meta(BaseModel.Meta):
        verbose_name = "enquiry"
        verbose_name_plural = "enquiries"
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [models.Index(fields=["ip_hash", "created_at"])]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"
