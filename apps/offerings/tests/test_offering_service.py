"""OfferingService with a fake repository: no database."""

from apps.offerings.models import Service
from apps.offerings.services.offering_service import OfferingService


class FakeRepo:
    def __init__(self, services):
        self.services = services

    def _published(self):
        return sorted((s for s in self.services if s.is_published), key=lambda s: s.sort_order)

    def published_services(self):
        return self._published()

    def home_services(self):
        return [s for s in self._published() if s.show_on_home]


def svc(title, order, home=True, published=True):
    return Service(title=title, sort_order=order, show_on_home=home, is_published=published)


def test_home_cards_are_published_home_services_in_order():
    repo = FakeRepo(
        [
            svc("B", 20),
            svc("A", 10),
            svc("Off home", 5, home=False),
            svc("Draft", 1, published=False),
        ]
    )
    assert [s.title for s in OfferingService(repo).home_cards()] == ["A", "B"]


def test_home_shows_at_most_six():
    repo = FakeRepo([svc(f"S{i}", i) for i in range(8)])
    assert [s.title for s in OfferingService(repo).home_cards()] == [f"S{i}" for i in range(6)]


def test_all_is_every_published_service():
    repo = FakeRepo([svc("B", 2, home=False), svc("A", 1), svc("Draft", 0, published=False)])
    assert [s.title for s in OfferingService(repo).all()] == ["A", "B"]
