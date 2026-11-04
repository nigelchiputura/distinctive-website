"""Home: hero slider, then the page's sections (one of them shows the service cards)."""

from django.http import HttpRequest, HttpResponse

from apps.core.controllers.base import BaseController
from apps.offerings.services.offering_service import OfferingService
from apps.pages.services.page_service import PageService


class HomeController(BaseController):
    template_name = "pages/home.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        content = PageService().get_page("home")
        return self.render_page(
            request,
            self.template_name,
            {"content": content, "service_cards": OfferingService().home_cards()},
        )
