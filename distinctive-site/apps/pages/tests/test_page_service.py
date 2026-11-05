"""PageService with a fake repository: no database."""

import pytest

from apps.core.exceptions import NotFoundError
from apps.pages.models import HeroSlide, Page, PageSection
from apps.pages.services.page_service import PageService


class FakeRepo:
    """Holds pages, sections and slides in memory; filters and orders like the real one."""

    def __init__(self, pages=(), sections=(), slides=()):
        self.pages = list(pages)
        self.sections = list(sections)
        self.slides = list(slides)

    def published_page(self, slug):
        return next((p for p in self.pages if p.slug == slug and p.is_published), None)

    def published_sections(self, page):
        rows = [s for s in self.sections if s.page is page and s.is_published]
        return sorted(rows, key=lambda s: s.sort_order)

    def published_slides(self, page):
        rows = [s for s in self.slides if s.page is page and s.is_published]
        return sorted(rows, key=lambda s: s.sort_order)


HOME = Page(slug="home", title="Home", is_published=True)


def section(heading, order, published=True, page=HOME):
    return PageSection(page=page, heading=heading, sort_order=order, is_published=published)


def test_published_sections_only_in_order():
    repo = FakeRepo(
        pages=[HOME],
        sections=[section("B", 20), section("Hidden", 5, published=False), section("A", 10)],
    )
    content = PageService(repo).get_page("home")
    assert [s.heading for s in content.sections] == ["A", "B"]


def test_slides_come_with_the_page():
    slide = HeroSlide(page=HOME, heading="Welcome", sort_order=0, is_published=True)
    content = PageService(FakeRepo(pages=[HOME], slides=[slide])).get_page("home")
    assert content.slides == [slide]


def test_missing_page_is_not_found():
    with pytest.raises(NotFoundError):
        PageService(FakeRepo(pages=[HOME])).get_page("about")


def test_unpublished_page_is_not_found():
    draft = Page(slug="about", title="About", is_published=False)
    with pytest.raises(NotFoundError):
        PageService(FakeRepo(pages=[draft])).get_page("about")


def test_title_and_description_fall_back():
    page = Page(slug="home", title="Home", is_published=True)
    content = PageService(FakeRepo(pages=[page])).get_page("home")
    assert content.title == "Home" and content.meta_description == ""
    page.meta_title, page.meta_description = "Distinctive", "HR consultancy"
    assert content.title == "Distinctive" and content.meta_description == "HR consultancy"
