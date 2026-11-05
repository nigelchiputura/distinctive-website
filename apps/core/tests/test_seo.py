"""Search and sharing tags, the sitemap, robots.txt and the error pages (Test Plan §3.6)."""

import json
import re

import pytest
from django.template.loader import render_to_string

from apps.core.services.seo_service import SeoService, absolute_url
from apps.core.services.site_details import DEFAULTS, SiteDetails, SocialLink
from apps.pages.models import Page

PAGES = {"/": "home", "/about/": "about", "/services/": "services", "/contact/": "contact"}


# ---- SeoService ----------------------------------------------------------------------------


def test_titles_canonical_and_image(settings):
    settings.SITE_URL = "https://distinctive.co.zw/"
    seo = SeoService(DEFAULTS).for_page(path="/about/", title="About Us")
    assert seo.title == "About Us | Distinctive Consultancy Services"
    assert seo.canonical == "https://distinctive.co.zw/about/"
    assert seo.image == "https://distinctive.co.zw/static/img/og-default.png"
    assert seo.description == DEFAULTS.meta_description and seo.noindex is False
    custom = SeoService(DEFAULTS).for_page(
        path="/", title="Home", meta_title="Our own title", description="Ours."
    )
    assert (custom.title, custom.description) == ("Our own title", "Ours.")


def test_noindex_follows_the_setting(settings):
    settings.SEO_NOINDEX = True
    assert SeoService(DEFAULTS).for_page(path="/", title="Home").noindex is True


def test_absolute_url_leaves_full_addresses(settings):
    settings.SITE_URL = "https://distinctive.co.zw"
    assert absolute_url("https://cdn.example.org/x.png") == "https://cdn.example.org/x.png"
    assert absolute_url("media/og.png") == "https://distinctive.co.zw/media/og.png"


def test_organization():
    site = SiteDetails(
        **{
            **DEFAULTS.__dict__,
            "social_links": (SocialLink("linkedin", "LinkedIn", "https://linkedin.com/x"),),
        }
    )
    org = SeoService(site).organization()
    assert org["@type"] == "Organization" and org["telephone"] == "+263242486642"
    assert org["address"]["streetAddress"] == "62 Mutare Road, Beverly, Msasa"
    assert org["address"]["addressLocality"] == "Harare"
    assert org["sameAs"] == ["https://linkedin.com/x"]
    assert "sameAs" not in SeoService(DEFAULTS).organization()  # no social URLs yet
    elsewhere = SiteDetails(**{**DEFAULTS.__dict__, "address": "1 Main Street, Bulawayo"})
    assert (
        SeoService(elsewhere).organization()["address"]["streetAddress"]
        == "1 Main Street, Bulawayo"
    )


# ---- the pages -----------------------------------------------------------------------------


def head(client, path):
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode().split("</head>")[0]


@pytest.mark.django_db
def test_each_page_has_its_own_title_description_and_canonical(client, settings):
    settings.SITE_URL = "https://distinctive.co.zw"
    for slug in PAGES.values():
        Page.objects.filter(slug=slug).update(meta_description=f"About {slug}.")
    titles, descriptions = set(), set()
    for path in PAGES:
        html = head(client, path)
        titles.add(re.search(r"<title>(.*?)</title>", html).group(1))
        descriptions.add(re.search(r'<meta name="description" content="(.*?)">', html).group(1))
        assert f'<link rel="canonical" href="https://distinctive.co.zw{path}">' in html
        assert '<meta property="og:image" content="https://distinctive.co.zw/static/' in html
        assert "noindex" not in html
    assert len(titles) == len(descriptions) == 4


@pytest.mark.django_db
def test_the_organization_is_on_home_only_and_escaped(client):
    from apps.core.models import SiteSettings

    SiteSettings.objects.update(tagline="</script><b>")
    home = head(client, "/")
    data = re.search(r'<script type="application/ld\+json">(.*?)</script>', home).group(1)
    assert "</script><b>" not in data and json.loads(data)["slogan"] == "</script><b>"
    assert "application/ld+json" not in head(client, "/about/")


@pytest.mark.django_db
def test_the_preview_host_is_noindex(client, settings):
    settings.SEO_NOINDEX = True
    assert '<meta name="robots" content="noindex, nofollow">' in head(client, "/")
    robots = client.get("/robots.txt").content.decode()
    assert robots == "User-agent: *\nDisallow: /\n"


@pytest.mark.django_db
def test_utility_pages_are_noindex(client):
    html = client.get("/accounts/login/").content.decode()
    assert '<meta name="robots" content="noindex">' in html and "canonical" not in html


# ---- sitemap and robots --------------------------------------------------------------------


@pytest.mark.django_db
def test_sitemap_lists_the_published_pages(client, settings):
    settings.SITE_URL = "https://distinctive.co.zw"
    Page.objects.filter(slug="about").update(is_published=False)
    response = client.get("/sitemap.xml")
    assert response.status_code == 200 and response["Content-Type"].startswith("application/xml")
    xml = response.content.decode()
    locs = re.findall(r"<loc>(.*?)</loc>", xml)
    assert locs == [
        "https://distinctive.co.zw/",
        "https://distinctive.co.zw/services/",
        "https://distinctive.co.zw/contact/",
    ]
    assert settings.ADMIN_URL_PATH not in xml and "<lastmod>20" in xml


@pytest.mark.django_db
def test_robots_points_to_the_sitemap_and_hides_the_admin(client, settings):
    settings.SITE_URL = "https://distinctive.co.zw"
    response = client.get("/robots.txt")
    text = response.content.decode()
    assert response["Content-Type"].startswith("text/plain")
    assert "Sitemap: https://distinctive.co.zw/sitemap.xml" in text
    assert "Disallow: /accounts/" in text and settings.ADMIN_URL_PATH not in text


# ---- error pages ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_an_unknown_address_gets_the_branded_404(client):
    response = client.get("/no-such-page/")
    assert response.status_code == 404
    html = response.content.decode()
    assert "We couldn't find that page" in html and 'href="/services/"' in html
    assert '<meta name="robots" content="noindex">' in html


def test_the_500_page_needs_no_request_or_database():
    html = render_to_string("500.html")  # what Django's server_error does: no context
    assert "Something went wrong on our side" in html and "/static/css/main.css" in html
    assert "enquiries@distinctive.co.zw" in html
