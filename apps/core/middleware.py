"""RedirectMiddleware: old WordPress addresses → their new pages (docs/architecture.md §7).

It only looks at responses that are a 404 for GET or HEAD, so it costs nothing on live pages
and can never hide one. It sits last in MIDDLEWARE, so it answers before CommonMiddleware
would add a trailing slash.
"""

from collections.abc import Callable

from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)

from apps.pages.services.redirect_service import RedirectService


class RedirectMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if response.status_code != 404 or request.method not in ("GET", "HEAD"):
            return response
        target = RedirectService().target_for(request.path, request.META.get("QUERY_STRING", ""))
        if target is None:
            return response
        redirect_class = HttpResponsePermanentRedirect if target.permanent else HttpResponseRedirect
        return redirect_class(target.url)
