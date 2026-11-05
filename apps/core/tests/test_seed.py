"""seed_site_content: adds what's missing, never changes what's there."""

import pytest
from django.core.management import call_command

from apps.core.exceptions import NotFoundError
from apps.core.seed import content
from apps.core.services.seed_service import SEED_IMAGES, SeedService
from apps.offerings.models import Service
from apps.pages.models import HeroSlide, Page, PageSection, Partner
from apps.team.models import TeamMember

# ---- with fakes: no database -------------------------------------------------------------


class FakePages:
    def __init__(self, slugs=("home", "about")):
        self.pages = {slug: Page(slug=slug, title=slug.title()) for slug in slugs}
        self.home = self.pages.get("home")
        self.sections, self.slides, self.updates = [], [], []

    def by_slug(self, slug):
        return self.pages.get(slug)

    def update(self, page, **data):
        self.updates.append((page.slug, data))

    def has_section(self, page, anchor):
        return any(p is page and s["anchor"] == anchor for p, s in self.sections)

    def add_section(self, page, **data):
        self.sections.append((page, data))

    def has_slide(self, page, heading):
        return any(s["heading"] == heading for s in self.slides)

    def add_slide(self, page, **data):
        self.slides.append(data)


class FakeByName:
    """Team or partners: rows keyed by name (and kind, for partners)."""

    def __init__(self, existing=()):
        self.rows = [dict(r) for r in existing]

    def by_name(self, *key):
        name = key[-1]
        return next((r for r in self.rows if r["name"] == name), None)

    def create(self, **data):
        self.rows.append(data)


class FakeServices:
    def __init__(self, existing=()):
        self.rows = [{"anchor": a} for a in existing]

    def by_anchor(self, anchor):
        return next((r for r in self.rows if r["anchor"] == anchor), None)

    def create(self, **data):
        self.rows.append(data)


def seeder(pages=None, services=None, team=None, partners=None):
    return SeedService(
        pages or FakePages(),
        services or FakeServices(),
        team or FakeByName(),
        partners or FakeByName(),
        open_image=lambda n: f"file:{n}",
    )


def test_first_run_adds_everything():
    pages, services = FakePages(), FakeServices()
    report = seeder(pages, services).seed()
    assert report.created == {
        "services": len(content.SERVICES),
        "team members": len(content.TEAM),
        "partners": len(content.PARTNERS),
        "hero slides": len(content.HOME_SLIDES),
        "sections": len(content.HOME_SECTIONS) + len(content.ABOUT_SECTIONS),
    }
    assert pages.updates == [
        ("home", {"meta_description": content.HOME_META_DESCRIPTION}),
        ("about", {"meta_description": content.ABOUT_META_DESCRIPTION}),
    ]
    proactive = next(s for _, s in pages.sections if s["anchor"] == "proactive")
    assert proactive["image"] == "file:proactive.jpg"
    story_page = next(p for p, s in pages.sections if s["anchor"] == "our-story")
    assert story_page.slug == "about"


def test_only_missing_items_are_added():
    services = FakeServices(existing=["hr-audits"])
    team = FakeByName(existing=[{"name": "Rose Nhamo"}])
    report = seeder(services=services, team=team).seed()
    assert report.created["services"] == len(content.SERVICES) - 1
    assert report.created["team members"] == len(content.TEAM) - 1


def test_an_existing_description_is_kept():
    pages = FakePages()
    pages.home.meta_description = "The client's own words"
    seeder(pages).seed()
    assert [slug for slug, _ in pages.updates] == ["about"]


@pytest.mark.parametrize("missing", ["home", "about"])
def test_each_page_must_exist(missing):
    slugs = tuple(s for s in ("home", "about") if s != missing)
    with pytest.raises(NotFoundError):
        seeder(FakePages(slugs)).seed()


def test_every_seed_image_exists():
    items = (
        *content.SERVICES,
        *content.HOME_SECTIONS,
        *content.HOME_SLIDES,
        *content.ABOUT_SECTIONS,
        *content.TEAM,
        *content.PARTNERS,
    )
    with_images = [i for i in items if i.get("image")]
    assert len(with_images) == 19
    assert all((SEED_IMAGES / i["image"]).is_file() for i in with_images)
    assert all(i.get("image_alt") for i in with_images)


# ---- the real command, twice ---------------------------------------------------------------


@pytest.mark.django_db
def test_command_is_idempotent_and_keeps_edits(settings, tmp_path, capsys):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_site_content")
    counts = (
        Service.objects.count(),
        PageSection.objects.count(),
        HeroSlide.objects.count(),
        TeamMember.objects.count(),
        Partner.objects.count(),
    )
    assert counts == (
        len(content.SERVICES),
        len(content.HOME_SECTIONS) + len(content.ABOUT_SECTIONS),
        len(content.HOME_SLIDES),
        len(content.TEAM),
        len(content.PARTNERS),
    )
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
        TeamMember.objects.count(),
        Partner.objects.count(),
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


@pytest.mark.django_db
def test_seeded_about_renders(settings, tmp_path, client):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_site_content")
    page = client.get("/about/").content.decode()
    assert '<h1 class="page-hero__heading">Bringing Excellence Into Your World!</h1>' in page
    for text in ("Our Story", "Strategic Partners", "Bindura University", "Capability Analysis"):
        assert text in page
    names = [m["name"] for m in content.TEAM]
    positions = [page.index(n) for n in names]
    assert positions == sorted(positions)  # all eight, in order
