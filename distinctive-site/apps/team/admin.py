"""Team admin (the leadership on About). Direct ORM: the documented admin exception."""

from django.contrib import admin
from django.db import models

from apps.core.admin_widgets import image_preview

from .models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "title", "sort_order", "is_published")
    list_display_links = ("thumbnail", "name")
    list_editable = ("sort_order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("name", "title", "bio")
    ordering = ("sort_order", "pk")
    readonly_fields = ("preview",)
    formfield_overrides = {models.URLField: {"assume_scheme": "https"}}  # noqa: RUF012
    fieldsets = (
        (None, {"fields": ("name", "title", "bio")}),
        ("Photo", {"fields": ("image", "preview", "image_alt", "image_decorative")}),
        ("Social media", {"fields": ("linkedin_url", "facebook_url")}),
        ("Where it shows", {"fields": ("sort_order", "is_published", "anchor")}),
    )

    @admin.display(description="")
    def thumbnail(self, obj: TeamMember) -> str:
        return image_preview(obj, height=40)

    @admin.display(description="current photo")
    def preview(self, obj: TeamMember) -> str:
        return image_preview(obj, height=120)
