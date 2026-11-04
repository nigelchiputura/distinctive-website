"""Small admin helpers shared by the content apps."""

from django.db.models import Model
from django.utils.html import format_html


def image_preview(obj: Model, height: int = 80) -> str:
    """A thumbnail of `obj.image` for list and inline screens; a dash when there's none."""
    image = getattr(obj, "image", None)
    if not image:
        return "—"
    return format_html(
        '<img src="{}" alt="" style="height:{}px;width:auto;border:1px solid #ddd">',
        image.url,
        height,
    )
