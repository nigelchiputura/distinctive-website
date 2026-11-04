"""PartnerService and PageBlocksService with fakes: no database."""

from apps.pages.models import PageSection, Partner
from apps.pages.services.page_blocks_service import PageBlocksService
from apps.pages.services.partner_service import PartnerService


class FakePartnerRepo:
    def __init__(self, rows):
        self.rows = rows

    def published_of_kind(self, kind):
        rows = [r for r in self.rows if r.kind == kind and r.is_published]
        return sorted(rows, key=lambda r: r.sort_order)


def logo(name, kind, order=0, published=True):
    return Partner(name=name, kind=kind, sort_order=order, is_published=published)


def test_partners_and_clients_split_by_kind_published_only():
    repo = FakePartnerRepo(
        [
            logo("Uni", "partner", 2),
            logo("Growth", "partner", 1),
            logo("Bank", "client"),
            logo("Draft", "partner", published=False),
        ]
    )
    service = PartnerService(repo)
    assert [p.name for p in service.partners()] == ["Growth", "Uni"]
    assert [p.name for p in service.clients()] == ["Bank"]


class Recorder:
    """Stands in for the offerings, partner and team services; records what was fetched."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def fetch():
            self.calls.append(name)
            return [name]

        return fetch


def sections(*types):
    return [PageSection(section_type=t) for t in types]


def test_blocks_are_fetched_only_for_the_section_types_used():
    rec = Recorder()
    blocks = PageBlocksService(offerings=rec, partners=rec, team=rec)
    assert blocks.for_sections(sections("band_light", "team", "partners")) == {
        "partners": ["partners"],
        "team": ["leadership"],
    }
    assert sorted(rec.calls) == ["leadership", "partners"]


def test_home_cards_and_clients():
    rec = Recorder()
    blocks = PageBlocksService(offerings=rec, partners=rec, team=rec)
    assert blocks.for_sections(sections("service_cards", "clients")) == {
        "service_cards": ["home_cards"],
        "clients": ["clients"],
    }


def test_a_page_without_blocks_fetches_nothing():
    rec = Recorder()
    assert (
        PageBlocksService(offerings=rec, partners=rec, team=rec).for_sections(sections("cta")) == {}
    )
    assert rec.calls == []
