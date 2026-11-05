"""Enquiries in the admin: read-only, filterable, with "Mark as handled" and "Resend notification
email". Direct ORM for listing is the documented admin exception; the actions go through
ContactService."""

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from apps.contact.services.contact_service import ContactService

from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "email", "source_page", "email_sent", "handled")
    list_filter = ("email_sent", "handled", "source_page")
    search_fields = ("name", "email", "message")
    date_hierarchy = "created_at"
    actions = ("mark_handled", "resend_notification")
    fields = (
        "created_at",
        "source_page",
        "name",
        "email",
        "phone",
        "message",
        "email_sent",
        "emailed_at",
        "email_error",
        "handled",
        "handled_at",
    )
    readonly_fields = fields

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False  # enquiries come only from the website's forms

    @admin.action(description="Mark as handled", permissions=["change"])
    def mark_handled(self, request: HttpRequest, queryset: QuerySet[ContactSubmission]) -> None:
        count = ContactService().mark_handled(list(queryset))
        self.message_user(request, f"Marked {count} enquiry(ies) as handled.")

    @admin.action(description="Resend notification email", permissions=["change"])
    def resend_notification(
        self, request: HttpRequest, queryset: QuerySet[ContactSubmission]
    ) -> None:
        service = ContactService()
        sent = failed = 0
        for submission in queryset:
            if service.resend(submission).email_sent:
                sent += 1
            else:
                failed += 1
        if sent:
            self.message_user(request, f"Sent {sent} notification email(s).")
        if failed:
            self.message_user(
                request,
                f"{failed} email(s) still couldn't be sent. The error is on each enquiry.",
                level=messages.ERROR,
            )
