"""Smoke tests against the real database."""

import pytest
from django.conf import settings


@pytest.mark.django_db
def test_healthz_reports_the_database(client):
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response.json() == {"db": "ok"}


@pytest.mark.django_db
def test_placeholder_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Distinctive Consultancy Services" in response.content


@pytest.mark.django_db
def test_admin_login_goes_to_the_sign_in_page(client):
    response = client.get(f"/{settings.ADMIN_URL_PATH}login/")
    assert response.status_code == 302 and response.url.startswith("/accounts/login/")


def test_requirements_only_grow():
    """base.txt → prod.txt → dev.txt, each including the one before (Development_Conventions §8)."""
    req = settings.BASE_DIR / "requirements"
    assert "-r base.txt" in (req / "prod.txt").read_text()
    assert "-r prod.txt" in (req / "dev.txt").read_text()
