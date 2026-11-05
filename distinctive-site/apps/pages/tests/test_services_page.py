"""The Services page through the real stack."""

import pytest
from django.core.management import call_command

from apps.core.seed import content
from apps.offerings.models import Service
from apps.pages.models import Page, PageSection, Partner

pytestmark = pytest.mark.django_db


@pytest.fixture
def services_page():
    return Page.objects.get(slug="services")


def html(client) -> str:
    response = client.get("/services/")
    assert response.status_code == 200
    return response.content.decode()


def test_services_works_on_a_fresh_database(client):
    page = html(client)
    assert '<h1 class="visually-hidden">Services</h1>' in page
    assert 'aria-current="page">Services</a>' in page


def test_every_published_service_gets_a_band_and_a_link(client, services_page):
    PageSection.objects.create(
        page=services_page, section_type="service_bands", heading="What We Do"
    )
    Service.objects.create(title="HR Audits", body="Audits **matter**.", sort_order=2)
    Service.objects.create(title="Team Building", body="Teams.", sort_order=1)
    Service.objects.create(title="Retired", is_published=False)
    page = html(client)
    assert page.index('id="team-building"') < page.index('id="hr-audits"')
    assert 'href="#hr-audits"' in page and 'href="#team-building"' in page
    assert "Retired" not in page and "<strong>matter</strong>" in page
    assert "band--black" in page and "band--white service-band--light" in page  # alternating


def test_a_service_image_shows_on_the_page_only_when_ticked(client, services_page):
    PageSection.objects.create(page=services_page, section_type="service_bands")
    kwargs = {"image": "services/x.jpg", "image_alt": "x", "image_width": 10, "image_height": 10}
    Service.objects.create(title="Card only", **kwargs)
    Service.objects.create(
        title="Diagram", image_on_services_page=True, **{**kwargs, "image_alt": "A diagram"}
    )
    page = html(client)
    assert 'alt="A diagram"' in page and 'alt="x"' not in page


def test_client_logos(client, services_page):
    PageSection.objects.create(page=services_page, section_type="clients", heading="Clients")
    Partner.objects.create(kind="client", name="TelOne")
    Partner.objects.create(kind="partner", name="A partner")
    page = html(client)
    assert "TelOne" in page and "A partner" not in page


def test_seeded_services_page(settings, tmp_path, client):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_site_content")
    page = html(client)
    assert '<h1 class="page-hero__heading">Our Services</h1>' in page
    for item in content.SERVICES:
        assert f'id="{item["anchor"]}"' in page and f'href="#{item["anchor"]}"' in page
    assert page.count('class="logo-grid__item"') == len(content.CLIENTS) == 10
    assert 'alt="Diagram of the five capacity development areas listed beside it"' in page


def test_home_card_links_land_on_a_band(settings, tmp_path, client):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_site_content")
    home = client.get("/").content.decode()
    services = html(client)
    for item in content.SERVICES:
        if item.get("show_on_home"):
            assert f'href="/services/#{item["anchor"]}"' in home
            assert f'id="{item["anchor"]}"' in services
