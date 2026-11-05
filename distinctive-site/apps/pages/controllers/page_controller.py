"""A page built from its sections: Home, About and Services (Contact adds its form on Day 8)."""

from typing import ClassVar

from django.http import HttpRequest, HttpResponse

from apps.core.controllers.base import BaseController
from apps.pages.services.page_blocks_service import PageBlocksService
from apps.pages.services.page_service import PageService


class PageController(BaseController):
    slug: ClassVar[str] = ""
    template_name: ClassVar[str] = "pages/page.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        content = PageService().get_page(self.slug)
        context = {"content": content, **PageBlocksService().for_sections(content.sections)}
        return self.render_page(request, self.template_name, context)


class HomeController(PageController):
    slug = "home"
    template_name = "pages/home.html"


class AboutController(PageController):
    slug = "about"


class ServicesController(PageController):
    slug = "services"
