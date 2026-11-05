"""Nothing from Google is in a page before consent (Test Plan §3.6, docs/frontend.md §7)."""

import pytest

from apps.core.seed import content
from apps.pages.models import Page, PageSection

pytestmark = pytest.mark.django_db

GOOGLE = ("googletagmanager", "maps.googleapis", "google.com/maps/embed")
PATHS = ("/", "/about/", "/services/", "/contact/")


@pytest.fixture
def contact_sections():
    page = Page.objects.get(slug="contact")
    for item in content.CONTACT_SECTIONS:
        PageSection.objects.create(page=page, **item)


@pytest.mark.parametrize("path", PATHS)
def test_no_google_address_in_the_initial_html(client, settings, contact_sections, path):
    settings.GA_MEASUREMENT_ID = "G-TEST123"
    response = client.get(path)
    assert response.status_code == 200
    page = response.content.decode()
    assert not [g for g in GOOGLE if g in page]
    assert 'data-ga-id="G-TEST123"' in page  # the banner carries the id for the script


def test_the_map_is_only_data_until_consent(client, contact_sections):
    page = client.get("/contact/").content.decode()
    assert 'data-consent-map data-map-key="test-maps-key"' in page
    assert "<iframe" not in page
    assert "maps/dir/?api=1&amp;destination=62%20Mutare%20Road" in page  # loads nothing itself


def test_without_a_key_the_map_band_shows_the_address_only(client, settings, contact_sections):
    settings.GOOGLE_MAPS_EMBED_KEY = ""
    page = client.get("/contact/").content.decode()
    assert "data-consent-map" not in page and "Get directions" in page


def test_no_banner_when_there_is_nothing_to_ask_about(client, settings):
    settings.GOOGLE_MAPS_EMBED_KEY = ""
    settings.GA_MEASUREMENT_ID = ""
    assert "data-cookie-banner" not in client.get("/").content.decode()


def test_the_banner_and_the_settings_link_wait_for_javascript(client):
    page = client.get("/").content.decode()
    assert "data-cookie-banner" in page
    assert "data-cookie-banner data-ga-id" in page and "hidden>" in page
    assert "data-cookie-settings hidden>Cookie settings</button>" in page
