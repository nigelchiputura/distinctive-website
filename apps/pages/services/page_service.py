"""A page's content for its controller: the page, its published sections and slides, in order."""

from dataclasses import dataclass, field

from apps.core.services.base import BaseService
from apps.pages.models import HeroSlide, Page, PageSection
from apps.pages.repositories.page_repository import PageRepository


@dataclass(frozen=True)
class PageContent:
    page: Page
    sections: list[PageSection] = field(default_factory=list)
    slides: list[HeroSlide] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.page.meta_title or self.page.title

    @property
    def meta_description(self) -> str:
        return self.page.meta_description


class PageService(BaseService):
    def __init__(self, repo: PageRepository | None = None):
        self.repo = repo or PageRepository()

    def get_page(self, slug: str) -> PageContent:
        """The published page with its published sections and slides; NotFoundError otherwise."""
        page = self.get_or_raise(self.repo.published_page(slug), f"No published page '{slug}'.")
        return PageContent(
            page=page,
            sections=self.repo.published_sections(page),
            slides=self.repo.published_slides(page),
        )
