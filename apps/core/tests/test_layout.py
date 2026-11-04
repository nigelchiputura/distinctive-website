"""The base layout: top bar, navbar, footer (Day 2)."""

import pytest

from apps.core.services.site_details import DEFAULTS, SiteDetails, SocialLink

pytestmark = pytest.mark.django_db


def test_layout_on_the_home_page(client):
    html = client.get("/").content.decode()
    assert 'href="/static/css/main.css"' in html
    assert 'href="#main"' in html and 'id="main"' in html  # skip link and its target
    for label in ("Home", "About Us", "Services", "Contact Us"):
        assert f">{label}</a>" in html
    assert 'href="tel:+263242486642"' in html
    assert "mailto:enquiries@distinctive.co.zw" in html
    assert "Reach Us" in html and "62 Mutare Road" in html
    assert "All rights reserved." in html


def test_current_page_is_marked_for_screen_readers(client):
    html = client.get("/").content.decode()
    assert 'class="nav-link active" href="/" aria-current="page">Home</a>' in html
    assert 'href="/about/" aria-current' not in html


def test_no_social_list_when_no_urls(client):
    assert 'aria-label="Social media"' not in client.get("/").content.decode()


def test_social_icons_render_when_urls_are_set(client, monkeypatch):
    with_facebook = SiteDetails(
        **{
            **DEFAULTS.__dict__,
            "social_links": (SocialLink("facebook", "Facebook", "https://facebook.com/x"),),
        }
    )
    monkeypatch.setattr("apps.core.context_processors.DEFAULTS", with_facebook)
    html = client.get("/").content.decode()
    assert 'href="https://facebook.com/x"' in html
    assert 'class="icon"' in html


def test_no_jobs_link_in_phase_1(client):
    assert 'href="/jobs/"' not in client.get("/").content.decode()
