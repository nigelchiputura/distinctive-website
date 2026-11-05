"""Loads the old site's content into an empty or partly filled database
(`manage.py seed_site_content`, docs/deployment.md §2.1).

Adds only what is missing, judged by each item's key (see apps/core/seed/content.py). It never
changes or removes what is already there, so it is safe to run again, and an editor's changes
survive it. An item an editor has deleted does come back on a re-run: run it on the first deploy.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django.core.files import File

from apps.core.seed import content
from apps.core.services.base import BaseService
from apps.offerings.repositories.service_repository import ServiceRepository
from apps.pages.repositories.page_repository import PageRepository
from apps.pages.repositories.partner_repository import PartnerRepository
from apps.team.repositories.team_repository import TeamRepository

SEED_IMAGES = Path(__file__).resolve().parent.parent / "seed" / "images"


def open_seed_image(name: str) -> File:
    """A seed image as a file Django can save into an ImageField."""
    return File((SEED_IMAGES / name).open("rb"), name=name)


@dataclass
class SeedReport:
    created: dict[str, int] = field(default_factory=dict)

    def add(self, kind: str) -> None:
        self.created[kind] = self.created.get(kind, 0) + 1

    @property
    def total(self) -> int:
        return sum(self.created.values())


class SeedService(BaseService):
    def __init__(
        self,
        pages: PageRepository | None = None,
        services: ServiceRepository | None = None,
        team: TeamRepository | None = None,
        partners: PartnerRepository | None = None,
        open_image: Callable[[str], Any] = open_seed_image,
    ):
        self.pages = pages or PageRepository()
        self.services = services or ServiceRepository()
        self.team = team or TeamRepository()
        self.partners = partners or PartnerRepository()
        self.open_image = open_image

    def seed(self) -> SeedReport:
        report = SeedReport()
        self._seed_services(report)
        self._seed_team(report)
        self._seed_partners(report)
        self._seed_page(
            report,
            "home",
            content.HOME_META_DESCRIPTION,
            content.HOME_SECTIONS,
            content.HOME_SLIDES,
        )
        self._seed_page(report, "about", content.ABOUT_META_DESCRIPTION, content.ABOUT_SECTIONS)
        return report

    # ---- parts -----------------------------------------------------------------------------

    def _seed_services(self, report: SeedReport) -> None:
        for item in content.SERVICES:
            if self.services.by_anchor(item["anchor"]) is None:
                self.services.create(**self._with_image(item))
                report.add("services")

    def _seed_team(self, report: SeedReport) -> None:
        for item in content.TEAM:
            if self.team.by_name(item["name"]) is None:
                self.team.create(**self._with_image(item))
                report.add("team members")

    def _seed_partners(self, report: SeedReport) -> None:
        for item in content.PARTNERS:
            if self.partners.by_name(item["kind"], item["name"]) is None:
                self.partners.create(**self._with_image(item))
                report.add("partners")

    def _seed_page(
        self,
        report: SeedReport,
        slug: str,
        meta_description: str,
        sections: tuple[dict[str, Any], ...],
        slides: tuple[dict[str, Any], ...] = (),
    ) -> None:
        page = self.get_or_raise(
            self.pages.by_slug(slug), f"The {slug} page is missing: run `manage.py migrate` first."
        )
        if not page.meta_description:
            self.pages.update(page, meta_description=meta_description)
        for item in slides:
            if not self.pages.has_slide(page, item["heading"]):
                self.pages.add_slide(page, **self._with_image(item))
                report.add("hero slides")
        for item in sections:
            if not self.pages.has_section(page, item["anchor"]):
                self.pages.add_section(page, **self._with_image(item))
                report.add("sections")

    def _with_image(self, item: dict[str, Any]) -> dict[str, Any]:
        """The item's fields, with its image file name replaced by the file itself."""
        data = dict(item)
        if data.get("image"):
            data["image"] = self.open_image(data["image"])
        return data
