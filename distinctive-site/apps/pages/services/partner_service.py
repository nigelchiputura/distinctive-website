"""Strategic partners (About) and corporate clients (Services)."""

from apps.core.services.base import BaseService
from apps.pages.models import Partner
from apps.pages.repositories.partner_repository import PartnerRepository


class PartnerService(BaseService):
    def __init__(self, repo: PartnerRepository | None = None):
        self.repo = repo or PartnerRepository()

    def partners(self) -> list[Partner]:
        return self.repo.published_of_kind(Partner.Kind.PARTNER)

    def clients(self) -> list[Partner]:
        return self.repo.published_of_kind(Partner.Kind.CLIENT)
