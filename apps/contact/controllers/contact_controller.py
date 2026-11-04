"""The Contact page, and where both enquiry forms post (docs/architecture.md §5).

GET shows the Contact page. POST takes either form: `form=contact` (the Contact page) or
`form=enquiry` (the gold block on Services, saved with source "services"). fetch() calls from
contact-form.js get the JSON envelope; a plain form post (JavaScript off) gets a redirect back
with a message, or the page again with the errors.
"""

import logging
from dataclasses import dataclass

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from apps.contact.forms import HONEYPOT_FIELD, ContactForm, EnquiryBaseForm, EnquiryForm
from apps.contact.models import ContactSubmission
from apps.contact.services.contact_service import ContactService
from apps.core.services.rate_limit_service import RateLimitService
from apps.core.services.site_settings_service import SiteSettingsService
from apps.pages.controllers.page_controller import PageController

logger = logging.getLogger(__name__)

SENT_MESSAGE = "Thank you, your message has been sent. We'll get back to you soon."


@dataclass(frozen=True)
class FormSpec:
    form_class: type[EnquiryBaseForm]
    source: str  # ContactSubmission.Source
    page_slug: str  # the page the form is on
    page_url: str  # its URL name


FORMS: dict[str, FormSpec] = {
    "contact": FormSpec(
        ContactForm, ContactSubmission.Source.CONTACT, "contact", "contact:contact"
    ),
    "enquiry": FormSpec(
        EnquiryForm, ContactSubmission.Source.SERVICES, "services", "pages:services"
    ),
}


class ContactController(PageController):
    slug = "contact"

    def post(self, request: HttpRequest) -> HttpResponse:
        kind = request.POST.get("form", "contact")
        spec = FORMS.get(kind) or FORMS["contact"]
        form = spec.form_class(request.POST)

        ip = self.client_ip(request)
        ident = ContactService.hash_ip(ip)
        limiter = RateLimitService(scope="contact")
        if limiter.is_limited(ident):
            return self._limited(request, spec, form)

        if request.POST.get(HONEYPOT_FIELD):
            # A bot: it is told the message was sent, and nothing is saved or emailed.
            logger.info("Enquiry dropped: the hidden field was filled in.")
            limiter.record(ident)
            return self._sent(request, spec, form)

        if not form.is_valid():
            return self._invalid(request, spec, form)

        ContactService().submit(
            form.for_service(),
            source_page=spec.source,
            ip=ip,
            user_agent=request.headers.get("user-agent", ""),
        )
        limiter.record(ident)
        return self._sent(request, spec, form)

    # ---- replies ---------------------------------------------------------------------------

    def _sent(self, request: HttpRequest, spec: FormSpec, form: EnquiryBaseForm) -> HttpResponse:
        if self.is_ajax(request):
            return self.json_ok({"message": SENT_MESSAGE})
        messages.success(request, SENT_MESSAGE, extra_tags=form.kind)
        return HttpResponseRedirect(f"{reverse(spec.page_url)}#{form.kind}-form")

    def _invalid(
        self, request: HttpRequest, spec: FormSpec, form: EnquiryBaseForm, status: int = 400
    ) -> HttpResponse:
        if self.is_ajax(request):
            return self.json_error(form.errors_for_json(), status=status)
        return self.render_sections(request, spec.page_slug, forms={form.kind: form}, status=status)

    def _limited(self, request: HttpRequest, spec: FormSpec, form: EnquiryBaseForm) -> HttpResponse:
        email = SiteSettingsService().get().enquiries_email
        message = (
            "You've sent us several messages in the last hour. Please try again later, "
            f"or email us at {email}."
        )
        if self.is_ajax(request):
            return self.json_error(message, status=429)
        form.errors  # noqa: B018  # validate first, so the message joins any field errors
        form.add_error(None, message)
        return self._invalid(request, spec, form, status=429)
