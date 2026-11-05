"""BaseController: the thin request handler every page and endpoint extends
(docs/architecture.md §4).

A controller parses the request, calls a service and returns HTML or JSON. It never touches a
repository or the ORM (apps/core/tests/test_layering.py). ServiceErrors raised by a service are
mapped to responses here, so individual controllers don't repeat try/except blocks.
"""

from typing import Any

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBase, JsonResponse
from django.shortcuts import render
from django.views import View

from apps.core.exceptions import NotFoundError, ServiceError


class BaseController(View):
    error_template = "core/error.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        try:
            return super().dispatch(request, *args, **kwargs)
        except ServiceError as exc:
            return self.handle_service_error(request, exc)

    # ---- responses -------------------------------------------------------------------------

    def render_page(
        self,
        request: HttpRequest,
        template: str,
        context: dict[str, Any] | None = None,
        status: int = 200,
    ) -> HttpResponse:
        return render(request, template, context or {}, status=status)

    @staticmethod
    def json_ok(data: Any = None, status: int = 200) -> JsonResponse:
        return JsonResponse({"ok": True, "data": data if data is not None else {}}, status=status)

    @staticmethod
    def json_error(errors: dict[str, list[str]] | str, status: int = 400) -> JsonResponse:
        if isinstance(errors, str):
            errors = {"__all__": [errors]}
        return JsonResponse({"ok": False, "errors": errors}, status=status)

    @staticmethod
    def is_ajax(request: HttpRequest) -> bool:
        """True for fetch() calls from our JS (http.js sets this header) or JSON-only clients."""
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return True
        accept = request.headers.get("accept", "")
        return "application/json" in accept and "text/html" not in accept

    # ---- error mapping ---------------------------------------------------------------------

    def handle_service_error(self, request: HttpRequest, exc: ServiceError) -> HttpResponse:
        if self.is_ajax(request):
            errors = exc.errors or {"__all__": [exc.message]}
            return self.json_error(errors, status=exc.status_code)
        if isinstance(exc, NotFoundError):
            # Django's own 404 handling, so the branded 404 page (Day 9) applies everywhere.
            raise Http404(exc.message) from exc
        return self.render_page(
            request,
            self.error_template,
            {"message": exc.message, "status": exc.status_code},
            status=exc.status_code,
        )
