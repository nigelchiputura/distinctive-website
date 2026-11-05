"""Where an old address goes now (docs/architecture.md §7). Used by RedirectMiddleware for
requests that would otherwise be a 404, and by `manage.py check_redirects`."""

from dataclasses import dataclass

from apps.core.services.base import BaseService
from apps.pages.models import Redirect
from apps.pages.paths import normalize_path
from apps.pages.repositories.redirect_repository import RedirectRepository


@dataclass(frozen=True)
class RedirectTarget:
    url: str
    permanent: bool


class RedirectService(BaseService):
    def __init__(self, repo: RedirectRepository | None = None):
        self.repo = repo or RedirectRepository()

    def find(self, path: str) -> Redirect | None:
        """The redirect for `path`: an exact match first, else the longest matching prefix."""
        path = normalize_path(path)
        exact = self.repo.active_exact(path)
        if exact is not None:
            return exact
        matches = [r for r in self.repo.active_prefixes() if path.startswith(r.old_path)]
        return max(matches, key=lambda r: len(r.old_path), default=None)

    def target_for(self, path: str, query: str = "", count: bool = True) -> RedirectTarget | None:
        """Where to send a request for `path`, or None. Never back to the same address."""
        redirect = self.find(path)
        if redirect is None:
            return None
        url = redirect.new_path
        if url.startswith("/") and normalize_path(url.split("#")[0]) == normalize_path(path):
            return None  # a loop: let the 404 stand
        if query and "?" not in url and "#" not in url:
            url = f"{url}?{query}"
        if count:
            self.repo.record_hit(redirect)
        return RedirectTarget(url=url, permanent=redirect.is_permanent)
