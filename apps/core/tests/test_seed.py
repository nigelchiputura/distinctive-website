"""seed_site_content: adds what's missing, never changes what's there."""

import pytest
from django.core.management import call_command

from apps.core.exceptions import NotFoundError
from apps.core.seed import content
from apps.core.services.seed_service import SEED_IMAGES, SeedService
from apps.offerings.models import Service
from apps.pages.models import HeroSlide, Page, PageSection

# ---- with fakes: no database -------------------------------------------------------------


class FakePages:
    def __init__(self, home=True):
        self.home = Page(slug="home", title="Home") if home else None
        self.sections, self.slides, self.updates = [], [], []

    def by_slug(self, slug):
        return self.home if slug == "home" else None

    def update(self, page, **data):
        self.updates.append(data)

    def has_section(self, page, anchor):
        return any(s["anchor"] == anchor for s in self.sections)

    def add_section(self, page, **data):
        self.sections.append(data)

    def has_slide(self, page, heading):
        return any(s["heading"] == heading for s in self.slides)

    def add_slide(self, page, **data):
        self.slides.append(data)


class FakeServices:
    def __init__(self, existing=()):
        self.rows = [{"anchor": a} for a in existing]

    def by_anchor(self, anchor):
        return next((r for r in self.rows if r["anchor"] == anchor), None)

    def create(self, **data):
        self.rows.append(data)


def seeder(pages=None, services=None):
    return SeedService(
        pages or FakePages(), services or FakeServices(), open_image=lambda n: f"file:{n}"
    )


def test_first_run_adds_everything():
    pages, services = FakePages(), FakeServices()
    report = seeder(pages, services).seed()
    assert report.created == {
        "services": len(content.SERVICES),
        "hero slides": len(content.HOME_SLIDES),
        "sections": len(content.HOME_SECTIONS),
    }
    assert pages.updates == [{"meta_description": content.HOME_META_DESCRIPTION}]
    proactive = next(s for s in pages.sections if s["anchor"] == "proactive")
    assert proactive["image"] == "file:proactive.jpg"


def test_only_missing_items_are_added():
    services = FakeServices(existing=["hr-audits"])
    report = seeder(services=services).seed()
    assert report.created["services"] == len(content.SERVICES) - 1


def test_an_existing_description_is_kept():
    pages = FakePages()
    pages.home.meta_description = "The client's own words"
    seeder(pages).seed()
    assert pages.updates == []


def test_home_page_must_exist():
    with pytest.raises(NotFoundError):
        seeder(FakePages(home=False)).seed()


def test_every_seed_image_exists():
    names = [
        i["image"]
        for i in (*content.SERVICES, *content.HOME_SECTIONS, *content.HOME_SLIDES)
        if i.get("image")
    ]
    assert names and all((SEED_IMAGES / n).is_file() for n in names)
    assert all(
        i.get("image_alt") for i in (*content.SERVICES, *content.HOME_SECTIONS) if i.get("image")
    )


# ---- the real command, twice ---------------------------------------------------------------


@pytest.mark.django_db
def test_command_is_idempotent_and_keeps_edits(settings, tmp_path, capsys):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_site_content")
    counts = (Service.objects.count(), PageSection.objects.count(), HeroSlide.objects.count())
    assert counts == (len(content.SERVICES), len(content.HOME_SECTIONS), len(content.HOME_SLIDES))
    assert (tmp_path / "services" / "hr-audits.jpg").is_file()
    assert Service.objects.get(anchor="hr-audits").image_width == 359

    hr = Service.objects.get(anchor="hr-audits")
    hr.summary = "Edited by the client"
    hr.save()

    call_command("seed_site_content")
    assert "Nothing to add" in capsys.readouterr().out
    assert (
        Service.objects.count(),
        PageSection.objects.count(),
        HeroSlide.objects.count(),
    ) == counts
    assert Service.objects.get(anchor="hr-audits").summary == "Edited by the client"


@pytest.mark.django_db
def test_seeded_home_renders(settings, tmp_path, client):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_site_content")
    page = client.get("/").content.decode()
    for text in (
        "Distinctive Consultancy Services",
        "HR Audits",
        "Get In Touch",
        "People Centred",
        "Proactive",
    ):
        assert text in page
    assert 'width="635" height="395"' in page  # stored image sizes reach the <img>
