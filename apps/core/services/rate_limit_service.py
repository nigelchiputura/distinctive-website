"""A fixed-window rate limit, counted in Django's cache (docs/architecture.md §5).

The cache is the database cache in development and production, so every gunicorn worker sees
the same counts. Callers pass an identifier that is already hashed (ContactService.hash_ip), so
no visitor's address is written to the cache table.
"""

from typing import Any

from django.conf import settings
from django.core.cache import caches

from apps.core.services.base import BaseService


class RateLimitService(BaseService):
    def __init__(
        self,
        scope: str,
        limit: int | None = None,
        window: int | None = None,
        cache: Any = None,
    ):
        self.scope = scope
        self.limit = settings.CONTACT_RATE_LIMIT if limit is None else limit
        self.window = settings.CONTACT_RATE_WINDOW if window is None else window
        self.cache = cache if cache is not None else caches["default"]

    def key(self, ident: str) -> str:
        return f"ratelimit:{self.scope}:{ident or 'unknown'}"

    def count(self, ident: str) -> int:
        return int(self.cache.get(self.key(ident), 0))

    def is_limited(self, ident: str) -> bool:
        """True once `ident` has used up its allowance for the current window."""
        return self.count(ident) >= self.limit

    def record(self, ident: str) -> int:
        """Count one more use. The window starts with the first use and lasts `window` seconds."""
        key = self.key(ident)
        if self.cache.add(key, 1, self.window):
            return 1
        try:
            return int(self.cache.incr(key))
        except ValueError:  # expired between add() and incr()
            self.cache.set(key, 1, self.window)
            return 1
