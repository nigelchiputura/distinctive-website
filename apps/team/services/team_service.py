"""The leadership team for About."""

from apps.core.services.base import BaseService
from apps.team.models import TeamMember
from apps.team.repositories.team_repository import TeamRepository


class TeamService(BaseService):
    def __init__(self, repo: TeamRepository | None = None):
        self.repo = repo or TeamRepository()

    def leadership(self) -> list[TeamMember]:
        """Published team members, in order."""
        return self.repo.published_members()
