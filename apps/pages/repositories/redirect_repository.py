"""Queries for old-site redirects."""

from django.db.models import F
from django.utils import timezone

from apps.core.repositories.base import BaseRepository
from apps.pages.models import Redirect


class RedirectRepository(BaseRepository[Redirect]):
    model = Redirect

    def active_exact(self, path: str) -> Redirect | None:
        return Redirect.objects.filter(is_active=True, old_path=path).first()

    def active_prefixes(self) -> list[Redirect]:
        return list(Redirect.objects.filter(is_active=True, match_prefix=True))

    def by_old_path(self, path: str) -> Redirect | None:
        return self.get_or_none(old_path=path)

    def record_hit(self, redirect: Redirect) -> None:
        """Counted in the database (F), so two requests at once both count."""
        Redirect.objects.filter(pk=redirect.pk).update(
            hits=F("hits") + 1, last_hit_at=timezone.now()
        )
