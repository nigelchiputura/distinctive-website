"""Markdown → sanitised HTML. The ONLY place HTML is made from admin-entered text
(docs/architecture.md §4). Everything that renders an editor's Markdown goes through here.

Two steps, in this order:
1. `markdown` turns the text into HTML. It passes raw HTML in the text straight through.
2. `nh3` (Rust's ammonia) keeps only the allow-listed tags, attributes and link schemes, and
   removes <script>/<style> with their contents. Its output is safe to mark as safe.
"""

import html as html_lib
import re

import markdown
import nh3

ALLOWED_TAGS = frozenset(
    {
        "p", "br", "hr",
        "h2", "h3", "h4", "h5", "h6",
        "strong", "em", "b", "i", "u", "s",
        "ul", "ol", "li",
        "blockquote", "code", "pre",
        "a",
        "table", "thead", "tbody", "tr", "th", "td",
    }
)  # fmt: skip
# No h1: each page has exactly one, its own title (docs/frontend.md §6).
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}, "th": {"align"}, "td": {"align"}}
ALLOWED_URL_SCHEMES = frozenset({"http", "https", "mailto", "tel"})
LINK_REL = "noopener noreferrer"
EXTENSIONS = ["sane_lists", "tables"]
_H1 = re.compile(r"<(/?)h1\b", re.IGNORECASE)


class MarkdownService:
    def render(self, text: str | None) -> str:
        """Sanitised HTML for `text`; an empty string for empty or None."""
        if not text or not text.strip():
            return ""
        html = markdown.markdown(text, extensions=EXTENSIONS, output_format="html")
        html = _H1.sub(r"<\1h2", html)  # "# Heading" becomes an h2; the page owns its h1
        return nh3.clean(
            html,
            tags=set(ALLOWED_TAGS),
            attributes={tag: set(attrs) for tag, attrs in ALLOWED_ATTRIBUTES.items()},
            url_schemes=set(ALLOWED_URL_SCHEMES),
            link_rel=LINK_REL,
        )

    def to_plain_text(self, text: str | None) -> str:
        """The text with all markup removed (for meta descriptions; Phase 2's search index)."""
        html = self.render(text)
        if not html:
            return ""
        plain = html_lib.unescape(nh3.clean(html, tags=set(), attributes={}))
        return " ".join(plain.split())  # plain text: escape it again wherever it's output
