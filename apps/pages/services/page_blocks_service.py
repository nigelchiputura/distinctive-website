"""What a page's sections need beyond their own fields.

Some section types show other content: service cards, partner or client logos, the team. This
service fetches each of those only when one of the page's sections uses it, so a page queries
for what it shows and nothing else, and an editor can put any of these blocks on any page.
"""

from collections.abc import Callable, Iterable
from typing import Any

from apps.core.services.base import BaseService
from apps.offerings.services.offering_service import OfferingService
from apps.pages.models import PageSection
from apps.pages.services.partner_service import PartnerService
from apps.team.services.team_service import TeamService

T = PageSection.SectionType


class PageBlocksService(BaseService):
    def __init__(
        self,
        offerings: OfferingService | None = None,
        partners: PartnerService | None = None,
        team: TeamService | None = None,
    ):
        offerings = offerings or OfferingService()
        partners = partners or PartnerService()
        team = team or TeamService()
        # section type → (context name, how to fetch it)
        self.sources: dict[str, tuple[str, Callable[[], Any]]] = {
            T.SERVICE_CARDS: ("service_cards", offerings.home_cards),
            T.PARTNERS: ("partners", partners.partners),
            T.CLIENTS: ("clients", partners.clients),
            T.TEAM: ("team", team.leadership),
        }

    def for_sections(self, sections: Iterable[PageSection]) -> dict[str, Any]:
        """{"partners": [...], "team": [...], …} for the block types these sections use."""
        used = {s.section_type for s in sections}
        return {name: fetch() for kind, (name, fetch) in self.sources.items() if kind in used}
