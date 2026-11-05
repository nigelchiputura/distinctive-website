"""NavigationService: pure logic, no database."""

import pytest

from apps.core.services.navigation_service import NavigationService


def labels(items):
    return [i.label for i in items]


def active(items):
    return [i.label for i in items if i.active]


def test_phase_1_items_in_order():
    items = NavigationService().items_for("/")
    assert labels(items) == ["Home", "About Us", "Services", "Contact Us"]


def test_no_jobs_in_phase_1():
    assert "Jobs" not in labels(NavigationService().items_for("/"))


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/", ["Home"]),
        ("/about/", ["About Us"]),
        ("/services/", ["Services"]),
        ("/contact/", ["Contact Us"]),
        ("/about/team/", ["About Us"]),  # below a section still marks it
        ("/unknown/", []),  # Home is active only on "/" itself
        ("/healthz/", []),
    ],
)
def test_active_item(path, expected):
    assert active(NavigationService().items_for(path)) == expected


def test_items_are_injectable():
    service = NavigationService(items=(("Home", "/"), ("Jobs", "/jobs/")))
    assert active(service.items_for("/jobs/12/")) == ["Jobs"]
