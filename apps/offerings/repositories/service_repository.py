"""Queries for the consulting services (the Service model, not a code "service")."""

from apps.core.repositories.base import BaseRepository
from apps.offerings.models import Service


class ServiceRepository(BaseRepository[Service]):
    model = Service

    def published_services(self) -> list[Service]:
        return list(self.published().order_by("sort_order", "pk"))

    def home_services(self) -> list[Service]:
        return list(self.published(show_on_home=True).order_by("sort_order", "pk"))

    def by_anchor(self, anchor: str) -> Service | None:
        return self.get_or_none(anchor=anchor)
