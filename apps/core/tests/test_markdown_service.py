"""MarkdownService: admin Markdown is rendered publicly, so these matter as much as any rule
(docs/Phase_1/Test_Plan.md §3.2)."""

import pytest
from django.template import Context, Template

from apps.core.services.markdown_service import MarkdownService

md = MarkdownService()


@pytest.mark.parametrize(
    ("source", "must_not_contain"),
    [
        ("<script>alert(1)</script>", ["<script", "alert(1)"]),
        ('<img src="x" onerror="alert(1)">', ["onerror", "<img"]),
        ('<b onclick="alert(1)">x</b>', ["onclick"]),
        ("[click](javascript:alert(1))", ["javascript:"]),
        ("[click](data:text/html;base64,PHNjcmlwdD4=)", ["data:"]),
        ('<iframe src="https://evil.example"></iframe>', ["<iframe"]),
        ("<style>body{display:none}</style>", ["<style", "display:none"]),
        ('<form action="https://evil.example"><input name="p"></form>', ["<form", "<input"]),
        ('<a href="https://x.example" style="color:red">x</a>', ["style="]),
    ],
)
def test_dangerous_markup_is_removed(source, must_not_contain):
    html = md.render(source)
    for bad in must_not_contain:
        assert bad not in html


def test_ordinary_formatting_survives():
    html = md.render(
        "## Our Story\n\nWe are **people centred** and *proactive*.\n\n"
        "- HR audits\n- Team building\n\n1. First\n2. Second\n\n> A quote"
    )
    for good in ("<h2>Our Story</h2>", "<strong>people centred</strong>", "<em>proactive</em>",
                 "<li>HR audits</li>", "<ol>", "<blockquote>"):  # fmt: skip
        assert good in html


def test_links_get_rel_and_safe_schemes_survive():
    html = md.render(
        "[site](https://distinctive.co.zw) [mail](mailto:enquiries@distinctive.co.zw) "
        "[call](tel:+263242486642)"
    )
    assert 'href="https://distinctive.co.zw"' in html
    assert 'href="mailto:enquiries@distinctive.co.zw"' in html
    assert 'href="tel:+263242486642"' in html
    assert html.count('rel="noopener noreferrer"') == 3


def test_an_h1_becomes_an_h2():
    """Each page has one h1, its own title (docs/frontend.md §6)."""
    assert md.render("# Heading") == "<h2>Heading</h2>"


def test_raw_html_text_is_escaped_not_rendered():
    html = md.render("1 < 2 & <notatag>")
    assert "<notatag>" not in html
    assert "&lt;" in html and "&amp;" in html


@pytest.mark.parametrize("empty", [None, "", "   \n  "])
def test_empty_input_gives_empty_output(empty):
    assert md.render(empty) == ""
    assert md.to_plain_text(empty) == ""


def test_plain_text():
    assert md.to_plain_text("## People\n\n**HR** audits & <b>more</b>") == "People HR audits & more"


def test_template_filter_renders_safely():
    out = Template("{% load core_extras %}{{ body|markdown }}").render(
        Context({"body": "**hi** <script>x()</script>"})
    )
    assert out == "<p><strong>hi</strong> </p>"
