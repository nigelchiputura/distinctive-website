"""Page admin: each page with its sections and hero slides inline (docs/users.md §5).
The admin uses the ORM directly: a documented exception to the layering."""

from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.db import models
from django.http import HttpRequest

from apps.core.admin_widgets import image_preview

from .models import HeroSlide, Page, PageSection, Partner

IMAGE_FIELDS = ("image", "preview", "image_alt", "image_decorative")


class PageSectionInline(admin.StackedInline):
    model = PageSection
    extra = 0
    ordering = ("sort_order", "pk")
    readonly_fields = ("preview",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "section_type",
                    "heading",
                    "heading_align",
                    "intro",
                    "body",
                    "sort_order",
                    "is_published",
                )
            },
        ),
        ("Image", {"fields": (*IMAGE_FIELDS, "image_position"), "classes": ("collapse",)}),
        (
            "Button and link name",
            {"fields": ("button_label", "button_url", "anchor"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="current image")
    def preview(self, obj: PageSection) -> str:
        return image_preview(obj, height=120)


class HeroSlideInline(admin.StackedInline):
    model = HeroSlide
    extra = 0
    ordering = ("sort_order", "pk")
    readonly_fields = ("preview",)
    fields = (
        "heading",
        "subheading",
        *IMAGE_FIELDS,
        "button_label",
        "button_url",
        "sort_order",
        "is_published",
    )

    @admin.display(description="current image")
    def preview(self, obj: HeroSlide) -> str:
        return image_preview(obj, height=120)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "section_count", "updated_at")
    readonly_fields = ("slug",)
    fieldsets = (
        (None, {"fields": ("title", "slug", "is_published")}),
        ("Search engines", {"fields": ("meta_title", "meta_description")}),
    )

    def get_inlines(self, request: HttpRequest, obj: Page | None) -> list[type[InlineModelAdmin]]:
        # Only Home has the slider (docs/frontend.md §4); other pages open with a hero_text section.
        if obj is not None and obj.slug == "home":
            return [HeroSlideInline, PageSectionInline]
        return [PageSectionInline]

    @admin.display(description="sections")
    def section_count(self, obj: Page) -> int:
        return obj.sections.count()

    # The four pages are fixed: the code finds each by its slug (pages.0002_the_four_pages).
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Page | None = None) -> bool:
        return False


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "kind", "sort_order", "is_published")
    list_display_links = ("thumbnail", "name")
    list_editable = ("sort_order", "is_published")
    list_filter = ("kind", "is_published")
    search_fields = ("name", "caption")
    ordering = ("kind", "sort_order", "pk")
    readonly_fields = ("preview",)
    formfield_overrides = {models.URLField: {"assume_scheme": "https"}}  # noqa: RUF012
    fieldsets = (
        (None, {"fields": ("kind", "name", "caption", "url")}),
        ("Logo", {"fields": ("image", "preview", "image_alt", "image_decorative")}),
        ("Where it shows", {"fields": ("sort_order", "is_published")}),
    )

    @admin.display(description="")
    def thumbnail(self, obj: Partner) -> str:
        return image_preview(obj, height=40)

    @admin.display(description="current logo")
    def preview(self, obj: Partner) -> str:
        return image_preview(obj, height=120)
