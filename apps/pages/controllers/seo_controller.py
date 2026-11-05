"""/sitemap.xml and /robots.txt (docs/frontend.md §3).

Both use SITE_URL, not the request's host. robots.txt doesn't name the admin: its address is
kept unguessable (ADMIN_URL_PATH), and listing it would publish it. The admin's pages aren't
indexed anyway: they redirect to the sign-in page, which says noindex.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from apps.core.controllers.base import BaseController
from apps.core.services.seo_service import absolute_url
from apps.pages.routes import page_path
from apps.pages.services.page_service import PageService


class SitemapController(BaseController):
    def get(self, request: HttpRequest) -> HttpResponse:
        entries = []
        for page in PageService().published_pages():
            path = page_path(page.slug)
            if path is not None:
                entries.append({"loc": absolute_url(path), "lastmod": page.updated_at.date()})
        response = self.render_page(request, "pages/sitemap.xml", {"entries": entries})
        response["Content-Type"] = "application/xml; charset=utf-8"
        return response


class RobotsController(BaseController):
    def get(self, request: HttpRequest) -> HttpResponse:
        if settings.SEO_NOINDEX:  # the preview host
            lines = ["User-agent: *", "Disallow: /"]
        else:
            lines = [
                "User-agent: *",
                "Disallow: /accounts/",
                "",
                f"Sitemap: {absolute_url('/sitemap.xml')}",
            ]
        return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")
