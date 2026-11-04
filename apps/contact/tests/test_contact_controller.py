"""ContactController: both forms, with and without JavaScript (Test Plan §3.3)."""

import pytest
from django.core import mail
from django.test import Client

from apps.contact.forms import ContactForm, EnquiryForm
from apps.contact.models import ContactSubmission
from apps.pages.models import Page, PageSection

pytestmark = pytest.mark.django_db

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest", "HTTP_ACCEPT": "application/json"}
CONTACT = {"form": "contact", "name": "Tendai M", "email": "t@example.com", "message": "Hello"}
ENQUIRY = {
    "form": "enquiry",
    "first_name": "Rudo",
    "last_name": "Moyo",
    "email": "r@example.com",
    "message": "An audit, please.",
}


@pytest.fixture(autouse=True)
def form_sections():
    PageSection.objects.create(
        page=Page.objects.get(slug="contact"), section_type="contact_form", heading="Get In Touch!"
    )
    PageSection.objects.create(
        page=Page.objects.get(slug="services"),
        section_type="enquiry_form",
        heading="Get In Touch With Us",
        button_label="Send enquiry",
    )


def post(client, data, ajax=True, **extra):
    return client.post("/contact/", data, **(AJAX if ajax else {}), **extra)


# ---- the page --------------------------------------------------------------------------


def test_contact_page_shows_the_form_and_the_details(client):
    page = client.get("/contact/").content.decode()
    assert 'id="contact-form"' in page and 'name="csrfmiddlewaretoken"' in page
    assert 'aria-current="page">Contact Us</a>' in page
    assert "Reach Us" in page and "recruitment@distinctive.co.zw" in page
    assert 'name="website"' in page  # the honeypot
    assert 'aria-describedby="contact-email-error"' in page


# ---- with JavaScript (the JSON envelope) -------------------------------------------------


def test_valid_ajax_post_saves_emails_and_answers_ok(client):
    response = post(client, CONTACT)
    assert response.status_code == 200
    assert response.json() == {"ok": True, "data": {"message": response.json()["data"]["message"]}}
    saved = ContactSubmission.objects.get()
    assert (saved.name, saved.source_page, saved.email_sent) == ("Tendai M", "contact", True)
    assert len(saved.ip_hash) == 64  # hashed, never the address itself
    assert mail.outbox[0].reply_to == ["t@example.com"]


def test_invalid_ajax_post_returns_the_field_errors(client):
    response = post(client, {**CONTACT, "email": "nope", "message": ""})
    assert response.status_code == 400
    errors = response.json()["errors"]
    assert errors["email"] == ["Please enter a valid email address, like name@example.com."]
    assert errors["message"] == ["Please enter your message."]
    assert not ContactSubmission.objects.exists()


def test_the_services_enquiry_is_stored_as_services(client):
    assert post(client, ENQUIRY).status_code == 200
    saved = ContactSubmission.objects.get()
    assert (saved.name, saved.source_page) == ("Rudo Moyo", "services")
    assert "(Services page)" in mail.outbox[0].subject


def test_an_unknown_form_name_is_treated_as_contact(client):
    assert post(client, {**CONTACT, "form": "other"}).status_code == 200
    assert ContactSubmission.objects.get().source_page == "contact"


def test_a_filled_honeypot_looks_like_success_but_saves_nothing(client):
    response = post(client, {**CONTACT, "website": "http://spam.example"})
    assert response.status_code == 200 and response.json()["ok"] is True
    assert not ContactSubmission.objects.exists() and not mail.outbox


def test_the_sixth_enquiry_in_an_hour_is_refused(client, settings):
    settings.CONTACT_RATE_LIMIT = 5
    for _ in range(5):
        assert post(client, CONTACT).status_code == 200
    response = post(client, CONTACT)
    assert response.status_code == 429
    assert "several messages in the last hour" in response.json()["errors"]["__all__"][0]
    assert ContactSubmission.objects.count() == 5


def test_the_limit_is_per_visitor(client, settings):
    settings.CONTACT_RATE_LIMIT = 1
    assert post(client, CONTACT, REMOTE_ADDR="198.51.100.1").status_code == 200
    assert post(client, CONTACT, REMOTE_ADDR="198.51.100.1").status_code == 429
    assert post(client, CONTACT, REMOTE_ADDR="198.51.100.2").status_code == 200


def test_invalid_posts_do_not_use_up_the_allowance(client, settings):
    settings.CONTACT_RATE_LIMIT = 1
    for _ in range(3):
        assert post(client, {**CONTACT, "email": ""}).status_code == 400
    assert post(client, CONTACT).status_code == 200


def test_a_failed_email_still_answers_ok(client, settings):
    settings.EMAIL_BACKEND = "apps.contact.tests.failing_backend.FailingBackend"
    assert post(client, CONTACT).status_code == 200
    saved = ContactSubmission.objects.get()
    assert saved.email_sent is False and saved.email_error


def test_a_post_without_a_csrf_token_is_refused():
    client = Client(enforce_csrf_checks=True)
    assert post(client, CONTACT).status_code == 403
    assert not ContactSubmission.objects.exists()


def test_a_post_with_the_csrf_header_is_accepted():
    client = Client(enforce_csrf_checks=True)
    client.get("/contact/")
    token = client.cookies["csrftoken"].value
    assert post(client, CONTACT, HTTP_X_CSRFTOKEN=token).status_code == 200


# ---- without JavaScript (normal form posts) ----------------------------------------------


def test_valid_post_redirects_back_with_a_message(client):
    response = post(client, CONTACT, ajax=False)
    assert response.status_code == 302 and response.url == "/contact/#contact-form"
    page = client.get(response.url).content.decode()
    assert "Thank you, your message has been sent." in page
    assert ContactSubmission.objects.count() == 1


def test_valid_enquiry_post_goes_back_to_services(client):
    response = post(client, ENQUIRY, ajax=False)
    assert response.url == "/services/#enquiry-form"
    page = client.get(response.url).content.decode()
    assert 'role="status"' in page and "Thank you" in page


def test_invalid_post_shows_the_page_again_with_the_errors(client):
    response = post(client, {**CONTACT, "name": ""}, ajax=False)
    assert response.status_code == 400
    page = response.content.decode()
    assert "Please enter your name." in page
    assert 'aria-invalid="true"' in page
    assert 'value="t@example.com"' in page  # what they typed is kept


def test_invalid_enquiry_post_shows_services_again(client):
    response = post(client, {**ENQUIRY, "last_name": ""}, ajax=False)
    assert response.status_code == 400
    page = response.content.decode()
    assert "Get In Touch With Us" in page and "Please enter your last name." in page


def test_rate_limited_post_explains_and_keeps_the_text(client, settings):
    settings.CONTACT_RATE_LIMIT = 0
    response = post(client, CONTACT, ajax=False)
    assert response.status_code == 429
    page = response.content.decode()
    assert "several messages in the last hour" in page and "enquiries@distinctive.co.zw" in page
    assert "Hello</textarea>" in page


# ---- the forms -----------------------------------------------------------------------------


def test_enquiry_form_joins_the_names():
    form = EnquiryForm({**ENQUIRY, "first_name": " Rudo ", "last_name": "Moyo "})
    assert form.is_valid()
    assert form.for_service()["name"] == "Rudo Moyo"


def test_message_length_is_capped():
    form = ContactForm({**CONTACT, "message": "x" * 5001})
    assert not form.is_valid()
    assert form.errors["message"] == ["Please keep your message under 5,000 characters."]
