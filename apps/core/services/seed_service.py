"""Loads the old site's content into an empty or partly filled database
(`manage.py seed_site_content`, docs/deployment.md §2.1).

Adds what is missing, judged by each item's key (see apps/core/seed/content.py). For an item that
is already there, it fills in only its **empty** text fields and a missing image, so a later day's
fuller content reaches a database seeded earlier, while anything an editor has filled in, ticked
or ordered is left alone. It never removes anything. Safe to run again; an item an editor has
deleted does come back on a re-run, so run it on the first deploy.
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
from apps.pages.repositories.redirect_repository import RedirectRepository
from apps.team.repositories.team_repository import TeamRepository

SEED_IMAGES = Path(__file__).resolve().parent.parent / "seed" / "images"


def open_seed_image(name: str) -> File:
    """A seed image as a file Django can save into an ImageField."""
    return File((SEED_IMAGES / name).open("rb"), name=name)


# Keys that identify an item, never "filled in".
# Fields items are found by, never rewritten. A section is found by its anchor, so an empty
# heading on it can be filled (Day 9 gave Home's service cards one).
KEY_FIELDS = frozenset({"anchor", "name", "kind", "old_path"})


def blank_fields(obj: Any, item: dict[str, Any]) -> dict[str, Any]:
    """The item's text and image values whose field on `obj` is still empty. Flags, numbers and
    keys are never touched (False and 0 are real choices, not blanks)."""
    blanks: dict[str, Any] = {}
    for name, value in item.items():
        if name in KEY_FIELDS or isinstance(value, bool | int):
            continue
        current = getattr(obj, name, None)
        if current is None or current == "":  # an empty FieldFile also equals ""
            blanks[name] = value
    return blanks


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
        redirects: RedirectRepository | None = None,
    ):
        self.pages = pages or PageRepository()
        self.services = services or ServiceRepository()
        self.team = team or TeamRepository()
        self.partners = partners or PartnerRepository()
        self.open_image = open_image
        self.redirects = redirects or RedirectRepository()

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
        self._seed_page(
            report, "services", content.SERVICES_META_DESCRIPTION, content.SERVICES_SECTIONS
        )
        self._seed_page(
            report, "contact", content.CONTACT_META_DESCRIPTION, content.CONTACT_SECTIONS
        )
        self._seed_redirects(report)
        return report

    # ---- parts -----------------------------------------------------------------------------

    def _seed_services(self, report: SeedReport) -> None:
        for item in content.SERVICES:
            self._add_or_fill(
                report,
                "services",
                self.services.by_anchor(item["anchor"]),
                item,
                self.services.create,
                self.services.update,
            )

    def _seed_team(self, report: SeedReport) -> None:
        for item in content.TEAM:
            self._add_or_fill(
                report,
                "team members",
                self.team.by_name(item["name"]),
                item,
                self.team.create,
                self.team.update,
            )

    def _seed_partners(self, report: SeedReport) -> None:
        for item in (*content.PARTNERS, *content.CLIENTS):
            label = "partners" if item["kind"] == "partner" else "clients"
            self._add_or_fill(
                report,
                label,
                self.partners.by_name(item["kind"], item["name"]),
                item,
                self.partners.create,
                self.partners.update,
            )

    def _seed_redirects(self, report: SeedReport) -> None:
        for item in content.REDIRECTS:
            self._add_or_fill(
                report,
                "redirects",
                self.redirects.by_old_path(item["old_path"]),
                item,
                self.redirects.create,
                self.redirects.update,
            )

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
        page_fields = {"meta_description": meta_description}
        if slug in content.META_TITLES:
            page_fields["meta_title"] = content.META_TITLES[slug]
        if blanks := blank_fields(page, page_fields):
            self.pages.update(page, **blanks)
        for item in slides:
            self._add_or_fill(
                report,
                "hero slides",
                self.pages.slide(page, item["heading"]),
                item,
                lambda **data: self.pages.add_slide(page, **data),
                self.pages.update,
            )
        for item in sections:
            self._add_or_fill(
                report,
                "sections",
                self.pages.section(page, item["anchor"]),
                item,
                lambda **data: self.pages.add_section(page, **data),
                self.pages.update,
            )

    def _add_or_fill(
        self,
        report: SeedReport,
        kind: str,
        existing: Any,
        item: dict[str, Any],
        create: Callable[..., Any],
        update: Callable[..., Any],
    ) -> None:
        if existing is None:
            create(**self._with_image(item))
            report.add(kind)
        elif blanks := blank_fields(existing, item):
            update(existing, **self._with_image(blanks))
            report.add("filled in")

    def _with_image(self, item: dict[str, Any]) -> dict[str, Any]:
        """The item's fields, with its image file name replaced by the file itself."""
        data = dict(item)
        if data.get("image"):
            data["image"] = self.open_image(data["image"])
        return data
