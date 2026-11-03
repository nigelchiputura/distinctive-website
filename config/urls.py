"""Root URLs. Each app adds its own urls.py as its pages arrive (Days 5–8)."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from apps.core.controllers.health_controller import HealthController
from apps.core.controllers.placeholder_controller import PlaceholderController

urlpatterns = [
    path(settings.ADMIN_URL_PATH, admin.site.urls),
    path("healthz/", HealthController.as_view(), name="healthz"),
    path("", PlaceholderController.as_view(), name="home"),
]

if settings.DEBUG:
    # Local uploads only; in production Caddy serves /media/ (docs/deployment.md §7).
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
