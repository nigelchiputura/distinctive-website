"""The single SiteSettings row."""

from apps.core.models import SiteSettings
from apps.core.repositories.base import BaseRepository


class SiteSettingsRepository(BaseRepository[SiteSettings]):
    model = SiteSettings

    def current(self) -> SiteSettings | None:
        return self.get_or_none(pk=SiteSettings.SINGLETON_PK)
