"""Values every page template needs: the site's details and the navigation."""

from datetime import date

from django.conf import settings
from django.http import HttpRequest

from apps.core.services.navigation_service import NavigationService
from apps.core.services.site_settings_service import SiteSettingsService


def site(request: HttpRequest) -> dict[str, object]:
    # "site_info", not "site": allauth's views put the django.contrib.sites record in the context
    # as "site", which silently replaced ours on the sign-in pages (Day 4).
    return {
        "site_info": SiteSettingsService().get(),
        "nav_items": NavigationService().items_for(request.path),
        "current_year": date.today().year,
        "google_login_enabled": settings.GOOGLE_LOGIN_ENABLED,
    }
