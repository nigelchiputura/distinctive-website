"""Template helpers. `{{ section.body|markdown }}` is the only way templates turn admin text into
HTML (docs/architecture.md §4)."""

from django import template
from django.utils.safestring import SafeString, mark_safe

from apps.core.services.markdown_service import MarkdownService

register = template.Library()
_markdown = MarkdownService()


@register.filter(name="markdown")
def markdown_filter(text: str | None) -> SafeString:
    # Safe to mark: MarkdownService's output is sanitised by nh3's allow-list.
    return mark_safe(_markdown.render(text))  # noqa: S308
