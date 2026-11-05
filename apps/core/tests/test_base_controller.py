"""BaseController: the JSON envelope and how ServiceErrors become responses."""

import json

import pytest
from django.http import Http404, HttpResponse
from django.test import RequestFactory
from django.utils.html import escape

from apps.core.controllers.base import BaseController
from apps.core.exceptions import ExternalServiceError, NotFoundError, ValidationError

rf = RequestFactory()
AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


def controller_raising(exc):
    class Failing(BaseController):
        def get(self, request):
            raise exc

    return Failing.as_view()


class Ok(BaseController):
    def get(self, request):
        return HttpResponse("fine")


def body(response):
    return json.loads(response.content)


def test_envelopes():
    assert body(BaseController.json_ok({"id": 1})) == {"ok": True, "data": {"id": 1}}
    assert body(BaseController.json_ok()) == {"ok": True, "data": {}}
    assert body(BaseController.json_error("Nope")) == {"ok": False, "errors": {"__all__": ["Nope"]}}
    assert BaseController.json_error({"email": ["Bad"]}, status=422).status_code == 422


def test_is_ajax():
    assert BaseController.is_ajax(rf.get("/", **AJAX))
    assert BaseController.is_ajax(rf.get("/", HTTP_ACCEPT="application/json"))
    assert not BaseController.is_ajax(rf.get("/", HTTP_ACCEPT="text/html,application/json"))
    assert not BaseController.is_ajax(rf.get("/"))


def test_no_error_passes_through():
    assert Ok.as_view()(rf.get("/")).content == b"fine"


@pytest.mark.parametrize(
    ("exc", "status"),
    [
        (NotFoundError(), 404),
        (ValidationError(errors={"email": ["Enter a valid email address."]}), 400),
        (ExternalServiceError(), 503),
    ],
)
def test_ajax_errors_become_json(exc, status):
    response = controller_raising(exc)(rf.get("/", **AJAX))
    assert response.status_code == status
    assert body(response)["ok"] is False


def test_validation_errors_keep_their_fields():
    exc = ValidationError(errors={"email": ["Enter a valid email address."]})
    assert body(controller_raising(exc)(rf.get("/", **AJAX)))["errors"] == {
        "email": ["Enter a valid email address."]
    }


def test_page_not_found_uses_djangos_404():
    with pytest.raises(Http404):
        controller_raising(NotFoundError())(rf.get("/"))


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("exc", "status"), [(ValidationError("Bad input."), 400), (ExternalServiceError(), 503)]
)
def test_page_errors_render_the_error_page(exc, status):
    response = controller_raising(exc)(rf.get("/"))
    assert response.status_code == status
    assert escape(exc.message) in response.content.decode()
