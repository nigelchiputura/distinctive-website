"""The consulting services for Home's cards and (Day 7) the Services page."""

from apps.core.services.base import BaseService
from apps.offerings.models import Service
from apps.offerings.repositories.service_repository import ServiceRepository

HOME_CARD_LIMIT = 6


class OfferingService(BaseService):
    def __init__(self, repo: ServiceRepository | None = None):
        self.repo = repo or ServiceRepository()

    def home_cards(self) -> list[Service]:
        """Published services ticked "show on Home", in order, at most six."""
        return self.repo.home_services()[:HOME_CARD_LIMIT]

    def all(self) -> list[Service]:
        """Every published service, in order."""
        return self.repo.published_services()
