"""The site's details for templates: the admin-edited row, with the defaults filling any gaps."""

from django.conf import settings

from apps.core.repositories.site_settings_repository import SiteSettingsRepository
from apps.core.services.base import BaseService
from apps.core.services.site_details import DEFAULTS, SiteDetails, SocialLink

# (SiteSettings field, SiteDetails field). Empty values fall back to DEFAULTS.
_TEXT_FIELDS = (
    "company_name",
    "tagline",
    "phone_display",
    "phone_href",
    "enquiries_email",
    "recruitment_email",
    "address",
    "hours",
    "footer_blurb",
    "meta_description",
    "map_query",
)
_SOCIAL = (
    ("facebook", "Facebook", "facebook_url"),
    ("linkedin", "LinkedIn", "linkedin_url"),
    ("instagram", "Instagram", "instagram_url"),
    ("x", "X (Twitter)", "x_url"),
)


class SiteSettingsService(BaseService):
    def __init__(self, repo: SiteSettingsRepository | None = None):
        self.repo = repo or SiteSettingsRepository()

    def get(self) -> SiteDetails:
        row = self.repo.current()
        if row is None:
            return self._with_env_analytics(DEFAULTS)

        values = {
            name: (getattr(row, name) or "").strip() or getattr(DEFAULTS, name)
            for name in _TEXT_FIELDS
        }
        social = tuple(
            SocialLink(name, label, (getattr(row, field) or "").strip())
            for name, label, field in _SOCIAL
        )
        og_image_url = row.og_image.url if row.og_image else DEFAULTS.og_image_url
        details = SiteDetails(
            **values,
            social_links=social,
            og_image_url=og_image_url,
            ga_measurement_id=(row.ga_measurement_id or "").strip(),
        )
        return self._with_env_analytics(details)

    @staticmethod
    def _with_env_analytics(details: SiteDetails) -> SiteDetails:
        """The admin's GA4 ID wins; otherwise the environment's (docs/frontend.md §7)."""
        if details.ga_measurement_id:
            return details
        env_id = getattr(settings, "GA_MEASUREMENT_ID", "")
        if not env_id:
            return details
        return SiteDetails(**{**details.__dict__, "ga_measurement_id": env_id})
