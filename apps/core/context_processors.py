"""Values every page template needs: the site's details and the navigation."""

from datetime import date

from django.http import HttpRequest

from apps.core.services.navigation_service import NavigationService
from apps.core.services.site_settings_service import SiteSettingsService


def site(request: HttpRequest) -> dict[str, object]:
    return {
        "site": SiteSettingsService().get(),
        "nav_items": NavigationService().items_for(request.path),
        "current_year": date.today().year,
    }
