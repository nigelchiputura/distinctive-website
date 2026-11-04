"""TeamService with a fake repository, and the model's anchors (database)."""

import pytest

from apps.team.models import TeamMember
from apps.team.repositories.team_repository import TeamRepository
from apps.team.services.team_service import TeamService


class FakeRepo:
    def __init__(self, members):
        self.members = members

    def published_members(self):
        rows = [m for m in self.members if m.is_published]
        return sorted(rows, key=lambda m: m.sort_order)


def test_leadership_is_published_members_in_order():
    repo = FakeRepo(
        [
            TeamMember(name="B", sort_order=2, is_published=True),
            TeamMember(name="Hidden", sort_order=0, is_published=False),
            TeamMember(name="A", sort_order=1, is_published=True),
        ]
    )
    assert [m.name for m in TeamService(repo).leadership()] == ["A", "B"]


@pytest.mark.django_db
def test_anchor_from_name_unique_and_stable():
    a = TeamMember.objects.create(name="Rose Nhamo", title="Director")
    b = TeamMember.objects.create(name="Rose Nhamo", title="Namesake")
    assert (a.anchor, b.anchor) == ("rose-nhamo", "rose-nhamo-2")
    a.name = "Rose N."
    a.save()
    a.refresh_from_db()
    assert a.anchor == "rose-nhamo"


@pytest.mark.django_db
def test_repository_orders_published_members():
    TeamMember.objects.create(name="Second", title="x", sort_order=2)
    TeamMember.objects.create(name="First", title="x", sort_order=1)
    TeamMember.objects.create(name="Draft", title="x", sort_order=0, is_published=False)
    repo = TeamRepository()
    assert [m.name for m in repo.published_members()] == ["First", "Second"]
    assert repo.by_name("Draft") is not None and repo.by_name("Nobody") is None
