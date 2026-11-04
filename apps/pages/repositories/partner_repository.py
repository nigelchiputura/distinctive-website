"""Queries for partner and client logos."""

from apps.core.repositories.base import BaseRepository
from apps.pages.models import Partner


class PartnerRepository(BaseRepository[Partner]):
    model = Partner

    def published_of_kind(self, kind: str) -> list[Partner]:
        return list(self.published(kind=kind).order_by("sort_order", "pk"))

    def by_name(self, kind: str, name: str) -> Partner | None:
        return self.get_or_none(kind=kind, name=name)
