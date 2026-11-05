"""Home through the real stack: from the database to the HTML, and the page admin."""

import re

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.offerings.models import Service
from apps.pages.models import HeroSlide, Page, PageSection
from apps.users.permissions import CONTENT_EDITOR

pytestmark = pytest.mark.django_db


@pytest.fixture
def home():
    return Page.objects.get(slug="home")


def html(client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    assert "pages/home.html" in [t.name for t in response.templates]
    return response.content.decode()


def test_home_works_on_a_fresh_database(client):
    page = html(client)
    assert '<h1 class="visually-hidden">Distinctive Consultancy Services</h1>' in page


def test_slide_heading_is_the_h1(client, home):
    HeroSlide.objects.create(page=home, heading="Bringing excellence", subheading="Into your world")
    page = html(client)
    assert '<h1 class="hero__heading">Bringing excellence</h1>' in page
    assert "data-hero-slider" not in page  # one slide: no carousel controls
    assert page.count("<h1") == 1


def test_several_slides_make_a_carousel(client, home):
    for n in range(3):
        HeroSlide.objects.create(page=home, heading=f"Slide {n}", sort_order=n)
    page = html(client)
    assert "data-hero-slider" in page and "data-hero-pause" in page
    assert page.count("<h1") == 1 and '<h2 class="hero__heading">Slide 2</h2>' in page


def test_sections_render_in_order_and_hidden_ones_dont(client, home):
    PageSection.objects.create(
        page=home, section_type="value_block", heading="Proactive", sort_order=20
    )
    PageSection.objects.create(
        page=home, section_type="value_block", heading="People Centred", sort_order=10
    )
    PageSection.objects.create(
        page=home, section_type="band_light", heading="Draft", is_published=False
    )
    page = html(client)
    assert page.index("People Centred") < page.index("Proactive")
    assert "Draft" not in page
    assert 'id="people-centred"' in page


def test_reordering_a_section_reorders_the_page(client, home):
    a = PageSection.objects.create(
        page=home, section_type="value_block", heading="Alpha", sort_order=10
    )
    PageSection.objects.create(page=home, section_type="value_block", heading="Beta", sort_order=20)
    a.sort_order = 30
    a.save()
    page = html(client)
    assert page.index("Beta") < page.index("Alpha")


def test_service_cards_link_to_their_band_on_services(client, home):
    PageSection.objects.create(page=home, section_type="service_cards")
    Service.objects.create(title="HR Audits", summary="Compliance audits.", show_on_home=True)
    Service.objects.create(title="Team Building", show_on_home=False)
    page = html(client)
    assert 'href="/services/#hr-audits"' in page and "Compliance audits." in page
    assert "Team Building" not in page
    # No section heading above, so the card titles are h2; the title's link covers the card.
    assert '<h2 class="service-card__title"><a class="service-card__link stretched-link" ' in page


def test_cta_and_markdown_body(client, home):
    PageSection.objects.create(
        page=home,
        section_type="cta",
        heading="Get the best",
        body="Call **today**<script>alert(1)</script>",
        button_label="Get In Touch",
        button_url="/contact/",
    )
    page = html(client)
    assert '<a class="btn btn-gold btn-lg" href="/contact/">Get In Touch <svg' in page
    assert "<strong>today</strong>" in page and "<script>alert" not in page


def test_unpublished_home_is_not_found(client, home):
    home.is_published = False
    home.save()
    assert client.get("/").status_code == 404


def test_page_title_and_description(client, home):
    home.meta_title, home.meta_description = "HR consultancy in Harare", "We help organisations."
    home.save()
    page = html(client)
    assert "<title>HR consultancy in Harare</title>" in page  # a search title is used as written
    assert '<meta name="description" content="We help organisations.">' in page


def test_no_multiline_hash_comments_in_templates():
    """{# … #} is single-line only: a multi-line one prints, or runs the tags inside it
    (errors-and-exceptions/multiline-template-comment-recursion__2026-11-03_1135)."""
    roots = [settings.BASE_DIR / "templates", *(settings.BASE_DIR / "apps").glob("*/templates")]
    unclosed_on_its_line = re.compile(r"\{#(?:(?!#\})[^\n])*\n")
    offenders = [
        str(path.relative_to(settings.BASE_DIR))
        for root in roots
        for path in root.rglob("*.html")
        if unclosed_on_its_line.search(path.read_text())
    ]
    assert offenders == []


def test_content_editor_can_edit_home_in_the_admin(client, home):
    editor = get_user_model().objects.create_user(
        "editor@distinctive.co.zw", "A-long-password-2026"
    )
    editor.is_staff = True
    editor.save()
    editor.groups.add(Group.objects.get(name=CONTENT_EDITOR))
    client.force_login(editor)
    admin = f"/{settings.ADMIN_URL_PATH}"
    page = client.get(f"{admin}pages/page/{home.pk}/change/")
    assert page.status_code == 200
    assert "Hero slides" in page.content.decode() and "Sections" in page.content.decode()
    assert client.get(f"{admin}offerings/service/").status_code == 200
    assert client.get(f"{admin}pages/page/add/").status_code == 403  # the four pages are fixed
