"""Health check: is the app able to reach its database?

Day 1's example of the layering: the controller calls this service, the service calls the
repository, and the test passes a fake repository (docs/architecture.md §3).
"""

import logging

from apps.core.repositories.health_repository import HealthRepository

logger = logging.getLogger(__name__)


class HealthService:
    def __init__(self, repo: HealthRepository | None = None):
        self.repo = repo or HealthRepository()

    def check(self) -> dict[str, str]:
        try:
            ok = self.repo.ping()
        except Exception:  # any database error means "not ok"; the detail goes to the log
            logger.exception("Health check: database unreachable")
            ok = False
        return {"db": "ok" if ok else "error"}

    def is_healthy(self, status: dict[str, str]) -> bool:
        return all(value == "ok" for value in status.values())
