"""Site settings admin: one row, never added twice or deleted (docs/users.md §5).
The admin uses the ORM directly: a documented exception to the layering."""

from django.contrib import admin
from django.db import models
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    # "facebook.com/x" typed without a scheme becomes https://… (Django 6's default too).
    formfield_overrides = {models.URLField: {"assume_scheme": "https"}}  # noqa: RUF012
    fieldsets = (
        ("Company", {"fields": ("company_name", "tagline", "footer_blurb")}),
        (
            "Contact details",
            {
                "fields": (
                    "phone_display",
                    "phone_href",
                    "enquiries_email",
                    "recruitment_email",
                    "address",
                    "hours",
                    "map_query",
                )
            },
        ),
        (
            "Social media",
            {
                "fields": ("facebook_url", "linkedin_url", "instagram_url", "x_url"),
                "description": "An icon shows on the website only for links filled in here.",
            },
        ),
        (
            "Search engines and analytics",
            {"fields": ("meta_description", "og_image", "ga_measurement_id")},
        ),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request: HttpRequest, obj: SiteSettings | None = None) -> bool:
        return False

    def changelist_view(self, request: HttpRequest, extra_context=None):
        """There is only one row, so the list goes straight to it."""
        row = SiteSettings.objects.first()
        if row is not None:
            return HttpResponseRedirect(reverse("admin:core_sitesettings_change", args=[row.pk]))
        return HttpResponseRedirect(reverse("admin:core_sitesettings_add"))
