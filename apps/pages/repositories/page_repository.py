"""Queries for pages, their sections and hero slides."""

from typing import Any

from apps.core.repositories.base import BaseRepository
from apps.pages.models import HeroSlide, Page, PageSection


class PageRepository(BaseRepository[Page]):
    model = Page

    def published_page(self, slug: str) -> Page | None:
        return self.published(slug=slug).first()

    def published_pages(self) -> list[Page]:
        return list(self.published().order_by("pk"))

    def by_slug(self, slug: str) -> Page | None:
        """Published or not (the seed command fills unpublished pages too)."""
        return self.get_or_none(slug=slug)

    def published_sections(self, page: Page) -> list[PageSection]:
        return list(
            PageSection.objects.filter(page=page, is_published=True).order_by("sort_order", "pk")
        )

    def published_slides(self, page: Page) -> list[HeroSlide]:
        return list(
            HeroSlide.objects.filter(page=page, is_published=True).order_by("sort_order", "pk")
        )

    # ---- used by the seed command ----------------------------------------------------------

    def section(self, page: Page, anchor: str) -> PageSection | None:
        return PageSection.objects.filter(page=page, anchor=anchor).first()

    def add_section(self, page: Page, **data: Any) -> PageSection:
        return PageSection.objects.create(page=page, **data)

    def slide(self, page: Page, heading: str) -> HeroSlide | None:
        return HeroSlide.objects.filter(page=page, heading=heading).first()

    def add_slide(self, page: Page, **data: Any) -> HeroSlide:
        return HeroSlide.objects.create(page=page, **data)
