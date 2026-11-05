"""BaseService: what every service shares (docs/architecture.md §4).

A service takes its repository through the constructor, with a real default, so tests can pass a
duck-typed fake (docs/architecture.md §3):

    class PageService(BaseService):
        def __init__(self, repo: PageRepository | None = None):
            self.repo = repo or PageRepository()
"""

from apps.core.exceptions import NotFoundError


class BaseService:
    @staticmethod
    def get_or_raise[T](value: T | None, message: str | None = None) -> T:
        """Return `value`, or raise NotFoundError when a lookup came back empty."""
        if value is None:
            raise NotFoundError(message)
        return value
