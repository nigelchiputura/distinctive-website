"""seed_site_content: adds what's missing, fills empty fields, never changes an editor's work."""

import pytest
from django.core.management import call_command

from apps.core.exceptions import NotFoundError
from apps.core.seed import content
from apps.core.services.seed_service import SEED_IMAGES, SeedService, blank_fields
from apps.offerings.models import Service
from apps.pages.models import HeroSlide, Page, PageSection, Partner
from apps.team.models import TeamMember

PAGES = ("home", "about", "services", "contact")


# ---- with fakes: no database -------------------------------------------------------------


class Row:
    """A stand-in for a saved model: attributes from a dict."""

    def __init__(self, **fields):
        self.__dict__.update(fields)


class FakeRows:
    """Services, team members or partners: rows found by one key field."""

    def __init__(self, key, existing=()):
        self.key, self.rows, self.updates = key, [Row(**r) for r in existing], []

    def find(self, value):
        return next((r for r in self.rows if getattr(r, self.key) == value), None)

    by_anchor = find

    def by_name(self, *key):
        return self.find(key[-1])

    def create(self, **data):
        self.rows.append(Row(**data))

    def update(self, row, **data):
        self.updates.append((row, data))
        row.__dict__.update(data)


class FakePages:
    def __init__(self, slugs=PAGES):
        self.pages = {slug: Page(slug=slug, title=slug.title()) for slug in slugs}
        self.sections, self.slides, self.updates = [], [], []

    def by_slug(self, slug):
        return self.pages.get(slug)

    def update(self, obj, **data):
        self.updates.append((getattr(obj, "slug", None), data))
        obj.__dict__.update(data)

    def section(self, page, anchor):
        return next((s for p, s in self.sections if p is page and s.anchor == anchor), None)

    def add_section(self, page, **data):
        self.sections.append((page, Row(**data)))

    def slide(self, page, heading):
        return next((s for s in self.slides if s.heading == heading), None)

    def add_slide(self, page, **data):
        self.slides.append(Row(**data))


def seeder(pages=None, services=None, team=None, partners=None):
    return SeedService(
        pages or FakePages(),
        services or FakeRows("anchor"),
        team or FakeRows("name"),
        partners or FakeRows("name"),
        open_image=lambda n: f"file:{n}",
    )


def test_first_run_adds_everything():
    pages = FakePages()
    report = seeder(pages).seed()
    assert report.created == {
        "services": len(content.SERVICES),
        "team members": len(content.TEAM),
        "partners": len(content.PARTNERS),
        "clients": len(content.CLIENTS),
        "hero slides": len(content.HOME_SLIDES),
        "sections": len(content.HOME_SECTIONS)
        + len(content.ABOUT_SECTIONS)
        + len(content.SERVICES_SECTIONS)
        + len(content.CONTACT_SECTIONS),
    }
    assert [slug for slug, _ in pages.updates] == list(PAGES)  # each page's meta description
    proactive = pages.section(pages.pages["home"], "proactive")
    assert proactive.image == "file:proactive.jpg"
    assert pages.section(pages.pages["about"], "our-story") is not None
    assert pages.section(pages.pages["services"], "services-list") is not None
    assert pages.section(pages.pages["services"], "get-in-touch").section_type == "enquiry_form"
    assert pages.section(pages.pages["contact"], "get-in-touch").section_type == "contact_form"


def test_existing_items_get_only_their_empty_fields_filled():
    services = FakeRows(
        "anchor",
        existing=[
            {  # as Day 5 left it: no body yet; an editor reworded the summary and untick Home
                "anchor": "hr-audits",
                "title": "HR Audits",
                "summary": "Edited by the client",
                "body": "",
                "image": "",
                "show_on_home": False,
                "sort_order": 99,
            }
        ],
    )
    report = seeder(services=services).seed()
    assert report.created["services"] == len(content.SERVICES) - 1
    assert report.created["filled in"] == 1
    hr = services.find("hr-audits")
    assert hr.body.startswith("**Distinctive Consultancy Services** provides")
    assert hr.image == "file:hr-audits.jpg"
    assert hr.summary == "Edited by the client"
    assert (hr.show_on_home, hr.sort_order) == (False, 99)  # flags and order are choices


def test_blank_fields_skips_keys_flags_and_numbers():
    row = Row(anchor="", title="Kept", body="", show_on_home=False, sort_order=0, image="")
    item = {
        "anchor": "a",
        "title": "T",
        "body": "B",
        "show_on_home": True,
        "sort_order": 5,
        "image": "i.jpg",
    }
    assert blank_fields(row, item) == {"body": "B", "image": "i.jpg"}


def test_an_existing_description_is_kept():
    pages = FakePages()
    pages.pages["home"].meta_description = "The client's own words"
    seeder(pages).seed()
    assert [slug for slug, _ in pages.updates] == ["about", "services", "contact"]


@pytest.mark.parametrize("missing", PAGES)
def test_each_page_must_exist(missing):
    with pytest.raises(NotFoundError):
        seeder(FakePages(tuple(s for s in PAGES if s != missing))).seed()


def test_every_seed_image_exists_and_has_a_description():
    items = (
        *content.SERVICES,
        *content.HOME_SECTIONS,
        *content.HOME_SLIDES,
        *content.ABOUT_SECTIONS,
        *content.SERVICES_SECTIONS,
        *content.CONTACT_SECTIONS,
        *content.TEAM,
        *content.PARTNERS,
        *content.CLIENTS,
    )
    with_images = [i for i in items if i.get("image")]
    assert len(with_images) == 30
    assert all((SEED_IMAGES / i["image"]).is_file() for i in with_images)
    assert all(i.get("image_alt") for i in with_images)
    assert len({i["anchor"] for i in content.SERVICES}) == len(content.SERVICES) == 13


# ---- the real command ----------------------------------------------------------------------


def counts():
    return (
        Service.objects.count(),
        PageSection.objects.count(),
        HeroSlide.objects.count(),
        TeamMember.objects.count(),
        Partner.objects.count(),
    )


@pytest.mark.django_db
def test_command_is_idempotent_and_keeps_edits(settings, tmp_path, capsys):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_site_content")
    assert counts() == (
        len(content.SERVICES),
        len(content.HOME_SECTIONS)
        + len(content.ABOUT_SECTIONS)
        + len(content.SERVICES_SECTIONS)
        + len(content.CONTACT_SECTIONS),
        len(content.HOME_SLIDES),
        len(content.TEAM),
        len(content.PARTNERS) + len(content.CLIENTS),
    )
    assert (tmp_path / "services" / "hr-audits.jpg").is_file()
    assert Service.objects.get(anchor="hr-audits").image_width == 359
    capsys.readouterr()

    hr = Service.objects.get(anchor="hr-audits")
    hr.summary = "Edited by the client"
    hr.save()

    before = counts()
    call_command("seed_site_content")
    assert "Nothing to add" in capsys.readouterr().out
    assert counts() == before
    assert Service.objects.get(anchor="hr-audits").summary == "Edited by the client"


@pytest.mark.django_db
def test_command_fills_in_a_database_seeded_earlier(settings, tmp_path, capsys):
    settings.MEDIA_ROOT = tmp_path
    Service.objects.create(anchor="hr-audits", title="HR Audits", summary="Day 5's summary")
    call_command("seed_site_content")
    out = capsys.readouterr().out
    assert "Filled in empty fields on 1 existing item(s)." in out
    hr = Service.objects.get(anchor="hr-audits")
    assert hr.summary == "Day 5's summary" and hr.body and hr.image


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


@pytest.mark.django_db
def test_seeded_contact_and_services_forms_render(settings, tmp_path, client):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_site_content")
    contact = client.get("/contact/").content.decode()
    assert '<h1 class="visually-hidden">Contact Us</h1>' in contact
    for text in ("Get In Touch!", "Reach Us", "recruitment@distinctive.co.zw", "Find Us"):
        assert text in contact
    services = client.get("/services/").content.decode()
    assert "Get In Touch With Us" in services and ">Send enquiry</button>" in services
    assert services.index("corporate-clients") < services.index('id="get-in-touch"')
