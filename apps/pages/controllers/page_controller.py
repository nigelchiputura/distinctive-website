"""A page built from its sections: Home, About, Services and Contact."""

from collections.abc import Iterable
from typing import Any, ClassVar

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from apps.contact.forms import ContactForm, EnquiryBaseForm, EnquiryForm
from apps.core.controllers.base import BaseController
from apps.pages.models import PageSection
from apps.pages.services.page_blocks_service import PageBlocksService
from apps.pages.services.page_service import PageService

T = PageSection.SectionType

# Section types that hold a form: (context name, the form's class).
FORM_SECTIONS: dict[str, tuple[str, type[EnquiryBaseForm]]] = {
    T.CONTACT_FORM: ("contact_form", ContactForm),
    T.ENQUIRY_FORM: ("enquiry_form", EnquiryForm),
}


class PageController(BaseController):
    slug: ClassVar[str] = ""
    template_name: ClassVar[str] = "pages/page.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return self.render_sections(request, self.slug, self.template_name)

    def render_sections(
        self,
        request: HttpRequest,
        slug: str,
        template_name: str = "pages/page.html",
        forms: dict[str, EnquiryBaseForm] | None = None,
        status: int = 200,
    ) -> HttpResponse:
        """The page `slug` with its blocks. `forms` replaces a section's empty form with a
        submitted one (shown with its errors)."""
        content = PageService().get_page(slug)
        context = {
            "content": content,
            **PageBlocksService().for_sections(content.sections),
            **self.form_context(content.sections, forms or {}),
        }
        return self.render_page(request, template_name, context, status=status)

    @staticmethod
    def form_context(
        sections: Iterable[PageSection], forms: dict[str, EnquiryBaseForm]
    ) -> dict[str, Any]:
        used = {s.section_type for s in sections}
        context: dict[str, Any] = {}
        for kind, (name, form_class) in FORM_SECTIONS.items():
            if kind in used:
                context[name] = forms.get(form_class.kind) or form_class()
        if T.MAP in used:
            context["maps_embed_key"] = settings.GOOGLE_MAPS_EMBED_KEY
        return context


class HomeController(PageController):
    slug = "home"
    template_name = "pages/home.html"


class AboutController(PageController):
    slug = "about"


class ServicesController(PageController):
    slug = "services"
