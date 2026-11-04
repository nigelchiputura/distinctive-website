"""Service admin (the consulting services). Direct ORM: the documented admin exception."""

from django.contrib import admin

from apps.core.admin_widgets import image_preview

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "title", "show_on_home", "sort_order", "is_published")
    list_display_links = ("thumbnail", "title")
    list_editable = ("show_on_home", "sort_order", "is_published")
    list_filter = ("show_on_home", "is_published")
    search_fields = ("title", "summary", "body")
    ordering = ("sort_order", "pk")
    readonly_fields = ("preview",)
    fieldsets = (
        (None, {"fields": ("title", "summary", "body")}),
        (
            "Image",
            {
                "fields": (
                    "image",
                    "preview",
                    "image_alt",
                    "image_decorative",
                    "image_on_services_page",
                )
            },
        ),
        ("Where it shows", {"fields": ("show_on_home", "sort_order", "is_published", "anchor")}),
    )

    @admin.display(description="")
    def thumbnail(self, obj: Service) -> str:
        return image_preview(obj, height=40)

    @admin.display(description="current image")
    def preview(self, obj: Service) -> str:
        return image_preview(obj, height=120)
