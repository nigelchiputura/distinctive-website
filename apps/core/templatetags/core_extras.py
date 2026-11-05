"""Template helpers. `{{ section.body|markdown }}` is the only way templates turn admin text into
HTML (docs/architecture.md §4)."""

import json

from django import template
from django.utils.safestring import SafeString, mark_safe

from apps.core.services.markdown_service import MarkdownService

register = template.Library()
_markdown = MarkdownService()


@register.filter(name="markdown")
def markdown_filter(text: str | None) -> SafeString:
    # Safe to mark: MarkdownService's output is sanitised by nh3's allow-list.
    return mark_safe(_markdown.render(text))  # noqa: S308


# The characters json_script escapes, so admin text can't close the <script> element.
_JSON_ESCAPES = {ord(">"): "\\u003E", ord("<"): "\\u003C", ord("&"): "\\u0026"}


@register.filter(name="jsonld")
def jsonld_filter(data: dict | None) -> SafeString:
    """`{{ seo.jsonld|jsonld }}` → a <script type="application/ld+json"> element (or nothing)."""
    if not data:
        return mark_safe("")
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":")).translate(_JSON_ESCAPES)
    return mark_safe(f'<script type="application/ld+json">{text}</script>')  # noqa: S308
