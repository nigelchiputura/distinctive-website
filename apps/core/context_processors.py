"""Values every page template needs: the site's details and the navigation."""

from datetime import date

from django.http import HttpRequest

from apps.core.services.navigation_service import NavigationService
from apps.core.services.site_details import DEFAULTS


def site(request: HttpRequest) -> dict[str, object]:
    return {
        # Day 3: SiteSettingsService().get() (the admin-edited values, falling back to DEFAULTS).
        "site": DEFAULTS,
        "nav_items": NavigationService().items_for(request.path),
        "current_year": date.today().year,
    }
