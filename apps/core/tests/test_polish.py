"""Day 9 polish: themes, labels, back to top and the reveal hooks (Test Plan §3.8)."""

import re

import pytest
from django.conf import settings

from apps.pages.models import Page, PageSection

pytestmark = pytest.mark.django_db

PATHS = ("/", "/about/", "/services/", "/contact/")


def html(client, path="/") -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


@pytest.mark.parametrize("path", PATHS)
def test_the_theme_is_applied_before_the_stylesheet_loads(client, path):
    page = html(client, path)
    head = page.split("</head>")[0]
    assert '<meta name="color-scheme" content="light dark">' in head
    # A file, not an inline script, and before the CSS, so a chosen theme never flashes.
    assert head.index("js/theme-init.js") < head.index("css/main.css")


def test_no_inline_scripts(client):
    """Every script is a file (JSON-LD is data, not code), so a strict Content-Security-Policy
    can be added later."""
    page = html(client)
    assert not re.search(r"<script(?![^>]*\bsrc=)(?![^>]*application/ld\+json)[^>]*>", page)


def test_theme_toggle_offers_system_light_and_dark(client):
    page = html(client)
    assert "data-theme-toggle hidden" in page  # shown by theme.js; CSS follows the system
    for choice in ("system", "light", "dark"):
        assert f'data-theme-choice="{choice}"' in page
    assert 'data-theme-choice="system" aria-pressed="true"' in page  # the default
    assert 'aria-label="Colour theme: System"' in page


def test_both_logos_are_in_the_navbar(client):
    page = html(client)
    assert 'class="brand-logo--light" src="/static/img/logo.png"' in page
    assert 'class="brand-logo--dark" src="/static/img/logo-dark.png"' in page
    assert (settings.BASE_DIR / "static" / "img" / "logo-dark.png").is_file()


def test_back_to_top_works_without_javascript(client):
    page = html(client)
    assert '<body id="top">' in page
    assert '<a class="back-to-top" href="#top" data-back-to-top aria-label="Back to top">' in page


def test_a_section_label_shows_above_its_heading(client):
    PageSection.objects.create(
        page=Page.objects.get(slug="about"),
        section_type="band_light",
        eyebrow="Who we are",
        heading="Our Story",
        body="Text.",
    )
    page = html(client, "/about/")
    label = page.index('<p class="eyebrow">Who we are</p>')
    assert label < page.index('<h2 class="band__heading">Our Story</h2>')


def test_sections_fade_in_only_with_javascript(client):
    """[data-reveal] is only a hook: nothing is hidden in the HTML itself."""
    PageSection.objects.create(
        page=Page.objects.get(slug="about"), section_type="band_light", heading="Hi", body="x"
    )
    page = html(client, "/about/")
    assert "data-reveal" in page and "reveal-ready" not in page and "is-visible" not in page


def test_footer_has_the_details_and_quick_links(client):
    page = html(client)
    footer = page.split('<footer class="site-footer">')[1]
    assert "Reach Us" in footer and "Quick Links" in footer
    assert 'aria-label="Footer"' in footer and 'href="/services/"' in footer
    assert "62 Mutare Road" in footer and "recruitment@" not in footer  # vacancies: Contact only
