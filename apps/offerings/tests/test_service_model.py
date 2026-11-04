"""Service anchors and the repository's queries (database)."""

import pytest

from apps.offerings.models import Service
from apps.offerings.repositories.service_repository import ServiceRepository

pytestmark = pytest.mark.django_db


def test_anchor_from_title_unique_and_stable():
    a = Service.objects.create(title="HR Audits")
    b = Service.objects.create(title="HR Audits")
    assert (a.anchor, b.anchor) == ("hr-audits", "hr-audits-2")
    a.title = "Human Resources Audits"
    a.save()
    a.refresh_from_db()
    assert a.anchor == "hr-audits"


def test_repository_filters_and_orders():
    Service.objects.create(title="Second", sort_order=2, show_on_home=True)
    Service.objects.create(title="First", sort_order=1, show_on_home=True)
    Service.objects.create(title="Not on home", sort_order=0)
    Service.objects.create(title="Draft", sort_order=0, show_on_home=True, is_published=False)
    repo = ServiceRepository()
    assert [s.title for s in repo.home_services()] == ["First", "Second"]
    assert [s.title for s in repo.published_services()] == ["Not on home", "First", "Second"]
    assert repo.by_anchor("first").title == "First"
