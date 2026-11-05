"""Queries for the leadership team."""

from apps.core.repositories.base import BaseRepository
from apps.team.models import TeamMember


class TeamRepository(BaseRepository[TeamMember]):
    model = TeamMember

    def published_members(self) -> list[TeamMember]:
        return list(self.published().order_by("sort_order", "pk"))

    def by_name(self, name: str) -> TeamMember | None:
        return self.get_or_none(name=name)
