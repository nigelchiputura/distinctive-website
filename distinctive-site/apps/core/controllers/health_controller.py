"""GET /healthz/ — JSON status for uptime monitors and the deploy checks."""

from django.http import HttpRequest, JsonResponse
from django.views import View

from apps.core.services.health_service import HealthService


class HealthController(View):
    service_class = HealthService

    def get(self, request: HttpRequest) -> JsonResponse:
        service = self.service_class()
        status = service.check()
        return JsonResponse(status, status=200 if service.is_healthy(status) else 503)
