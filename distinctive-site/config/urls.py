"""Root URLs. Each app adds its own urls.py as its pages arrive (Days 5–8)."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from apps.core.controllers.health_controller import HealthController

urlpatterns = [
    # One sign-in page for everyone: the admin's own login form redirects to allauth's, which
    # has Google sign-in and allauth's rate limiting (docs/users.md §3).
    path(
        f"{settings.ADMIN_URL_PATH}login/",
        RedirectView.as_view(pattern_name="account_login", query_string=True),
        name="admin_login_redirect",
    ),
    path(settings.ADMIN_URL_PATH, admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("healthz/", HealthController.as_view(), name="healthz"),
    path("", include("apps.pages.urls")),
]

if settings.DEBUG:
    # Local uploads only; in production Caddy serves /media/ (docs/deployment.md §7).
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
