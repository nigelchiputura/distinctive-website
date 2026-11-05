"""About through the real stack, and the team and partner admins."""

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.pages.models import Page, PageSection, Partner
from apps.team.models import TeamMember
from apps.users.permissions import CONTENT_EDITOR

pytestmark = pytest.mark.django_db


@pytest.fixture
def about():
    return Page.objects.get(slug="about")


def html(client) -> str:
    response = client.get("/about/")
    assert response.status_code == 200
    assert "pages/page.html" in [t.name for t in response.templates]
    return response.content.decode()


def test_about_works_on_a_fresh_database(client):
    page = html(client)
    assert '<h1 class="visually-hidden">About Us</h1>' in page
    assert 'aria-current="page">About Us</a>' in page


def test_a_leading_hero_band_is_the_h1(client, about):
    PageSection.objects.create(page=about, section_type="hero_text", heading="Bringing Excellence")
    PageSection.objects.create(page=about, section_type="hero_text", heading="Second", sort_order=5)
    page = html(client)
    assert '<h1 class="page-hero__heading">Bringing Excellence</h1>' in page
    assert '<h2 class="page-hero__heading">Second</h2>' in page
    assert page.count("<h1") == 1


def test_our_story_has_both_columns(client, about):
    PageSection.objects.create(
        page=about,
        section_type="two_column",
        heading="Our Story",
        intro="Founded in **2006**.",
        body="We grew across **Zambia**.",
    )
    page = html(client)
    assert "band--gradient" in page
    assert "<strong>2006</strong>" in page and "<strong>Zambia</strong>" in page


def test_partners_section_shows_published_partner_logos_only(client, about):
    PageSection.objects.create(page=about, section_type="partners", heading="Strategic Partners")
    Partner.objects.create(
        name="Emergence Growth", caption="Emergence Growth", url="https://example.org"
    )
    Partner.objects.create(name="Hidden", caption="Hidden", is_published=False)
    Partner.objects.create(name="A client", caption="A client", kind="client")
    page = html(client)
    assert "Emergence Growth" in page and 'href="https://example.org"' in page
    assert "Hidden" not in page and "A client" not in page


def test_team_section_in_order_with_bios_and_links(client, about):
    PageSection.objects.create(
        page=about, section_type="team", heading="Our Leadership", heading_align="center"
    )
    TeamMember.objects.create(name="Second Person", title="Board Member", sort_order=2)
    TeamMember.objects.create(
        name="First Person",
        title="Chair",
        bio="Holds an **MBA**.",
        linkedin_url="https://www.linkedin.com/in/example",
        sort_order=1,
    )
    TeamMember.objects.create(name="Former", title="x", is_published=False)
    page = html(client)
    assert page.index("First Person") < page.index("Second Person")
    assert "Former" not in page
    assert '<h3 class="team-card__name">First Person</h3>' in page
    assert 'id="first-person"' in page and "data-bio>" in page and "<strong>MBA</strong>" in page
    assert 'aria-label="First Person on LinkedIn (opens in a new tab)"' in page
    assert "Second Person on LinkedIn" not in page  # no URL, no icon
    assert "align-center" in page


def test_blocks_appear_only_where_a_section_asks_for_them(client, about):
    TeamMember.objects.create(name="Not on this page", title="x")
    assert "Not on this page" not in html(client)


def test_unpublished_about_is_not_found(client, about):
    about.is_published = False
    about.save()
    assert client.get("/about/").status_code == 404


def test_content_editor_can_edit_team_and_partners(client):
    editor = get_user_model().objects.create_user(
        "editor@distinctive.co.zw", "A-long-password-2026"
    )
    editor.is_staff = True
    editor.save()
    editor.groups.add(Group.objects.get(name=CONTENT_EDITOR))
    client.force_login(editor)
    admin = f"/{settings.ADMIN_URL_PATH}"
    assert client.get(f"{admin}team/teammember/").status_code == 200
    assert client.get(f"{admin}team/teammember/add/").status_code == 200
    assert client.get(f"{admin}pages/partner/").status_code == 200
