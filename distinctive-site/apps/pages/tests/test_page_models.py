"""Section anchors and image rules (database)."""

import pytest
from django.core.exceptions import ValidationError

from apps.pages.models import Page, PageSection

pytestmark = pytest.mark.django_db


@pytest.fixture
def home():
    return Page.objects.get(slug="home")


def test_the_four_pages_exist_after_migrate():
    assert list(Page.objects.values_list("slug", flat=True)) == [
        "home",
        "about",
        "services",
        "contact",
    ]


def test_anchor_comes_from_the_heading_and_is_unique_per_page(home):
    first = PageSection.objects.create(page=home, section_type="band_light", heading="Our Story")
    second = PageSection.objects.create(page=home, section_type="band_light", heading="Our Story")
    elsewhere = PageSection.objects.create(
        page=Page.objects.get(slug="about"), section_type="band_light", heading="Our Story"
    )
    assert (first.anchor, second.anchor, elsewhere.anchor) == (
        "our-story",
        "our-story-2",
        "our-story",
    )


def test_anchor_stays_when_the_heading_changes(home):
    s = PageSection.objects.create(page=home, section_type="band_light", heading="People Centred")
    s.heading = "People First"
    s.save()
    s.refresh_from_db()
    assert s.anchor == "people-centred"


def test_section_without_heading_gets_an_anchor_from_its_type(home):
    s = PageSection.objects.create(page=home, section_type="service_cards")
    assert s.anchor == "service-cards"


def test_an_image_needs_a_description_unless_decorative(home):
    s = PageSection(
        page=home,
        section_type="value_block",
        heading="X",
        image="pages/sections/x.jpg",
        image_width=10,
        image_height=10,  # no file needed
    )
    with pytest.raises(ValidationError) as exc:
        s.clean()
    assert "image_alt" in exc.value.message_dict
    s.image_decorative = True
    s.clean()
    assert s.alt_text == ""
    s.image_decorative, s.image_alt = False, "Two people talking"
    s.clean()
    assert s.alt_text == "Two people talking"
