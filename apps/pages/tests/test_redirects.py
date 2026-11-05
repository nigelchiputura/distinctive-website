"""Old-site redirects: the path rule, the model, the service, the middleware and the command."""

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command

from apps.pages.models import Redirect
from apps.pages.paths import normalize_path
from apps.pages.services.redirect_service import RedirectService

# ---- normalize_path ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("/about-us/", "/about-us/"),
        ("/About-Us", "/about-us/"),
        ("about-us", "/about-us/"),
        ("https://distinctive.co.zw/about-us/?utm=x#top", "/about-us/"),
        ("//double//slashes", "/double/slashes/"),
        ("/feed.xml", "/feed.xml"),
        ("/2021/08/receptionist/", "/2021/08/receptionist/"),
        ("/caf%C3%A9/", "/café/"),
        ("", "/"),
    ],
)
def test_normalize_path(raw, expected):
    assert normalize_path(raw) == expected


# ---- the service, with a fake repository ---------------------------------------------------


class Row:
    def __init__(self, old_path, new_path, match_prefix=False, is_permanent=True):
        self.old_path, self.new_path = old_path, new_path
        self.match_prefix, self.is_permanent = match_prefix, is_permanent


class FakeRedirects:
    def __init__(self, *rows):
        self.rows, self.hits = list(rows), []

    def active_exact(self, path):
        return next((r for r in self.rows if r.old_path == path), None)

    def active_prefixes(self):
        return [r for r in self.rows if r.match_prefix]

    def record_hit(self, redirect):
        self.hits.append(redirect.old_path)


def service(*rows):
    return RedirectService(FakeRedirects(*rows))


def test_exact_match_wins_and_is_counted():
    svc = service(Row("/about-us/", "/about/"), Row("/about-us/", "/other/", match_prefix=True))
    target = svc.target_for("/About-Us")
    assert (target.url, target.permanent) == ("/about/", True)
    assert svc.repo.hits == ["/about-us/"]


def test_the_longest_prefix_wins():
    svc = service(
        Row("/category/", "/", match_prefix=True),
        Row("/category/jobs/", "/contact/", match_prefix=True, is_permanent=False),
    )
    target = svc.target_for("/category/jobs/receptionist/")
    assert (target.url, target.permanent) == ("/contact/", False)
    assert svc.target_for("/category/news/").url == "/"


def test_a_prefix_needs_the_tick():
    assert service(Row("/jobs/", "/contact/")).target_for("/jobs/marketing-manager/") is None


def test_the_query_string_is_kept_unless_the_target_has_its_own():
    assert service(Row("/a/", "/b/")).target_for("/a/", "utm_source=x").url == "/b/?utm_source=x"
    assert service(Row("/a/", "/b/#x")).target_for("/a/", "q=1").url == "/b/#x"


def test_a_redirect_to_itself_is_ignored():
    assert service(Row("/about/", "/About")).target_for("/about/") is None


def test_count_false_counts_nothing():
    svc = service(Row("/a/", "/b/"))
    svc.target_for("/a/", count=False)
    assert svc.repo.hits == []


# ---- the model -----------------------------------------------------------------------------


def test_clean_normalises_and_checks_the_target():
    r = Redirect(old_path="https://distinctive.co.zw/About-Us", new_path=" /about/ ")
    r.clean()
    assert (r.old_path, r.new_path) == ("/about-us/", "/about/")
    with pytest.raises(ValidationError, match="Start with /"):
        Redirect(old_path="/a/", new_path="about").clean()
    with pytest.raises(ValidationError, match="to itself"):
        Redirect(old_path="/a/", new_path="/A").clean()
    Redirect(old_path="/a/", new_path="https://example.org/").clean()  # another site is fine


# ---- through the real stack ----------------------------------------------------------------


@pytest.fixture
def redirects(db):
    Redirect.objects.create(old_path="/About-Us", new_path="/about/")
    Redirect.objects.create(
        old_path="/jobs/", new_path="/contact/", match_prefix=True, is_permanent=False
    )
    Redirect.objects.create(old_path="/retired/", new_path="/", is_active=False)


@pytest.mark.django_db
def test_an_old_address_answers_301_and_is_counted(client, redirects):
    response = client.get("/about-us")
    assert response.status_code == 301 and response["Location"] == "/about/"
    saved = Redirect.objects.get(old_path="/about-us/")
    assert saved.hits == 1 and saved.last_hit_at is not None


@pytest.mark.django_db
def test_a_job_post_answers_302_to_contact(client, redirects):
    response = client.get("/jobs/receptionist/")
    assert response.status_code == 302 and response["Location"] == "/contact/"


@pytest.mark.django_db
def test_live_pages_inactive_redirects_and_posts_are_left_alone(client, redirects):
    Redirect.objects.create(old_path="/services/", new_path="/")
    assert client.get("/services/").status_code == 200  # a live page is never redirected
    assert client.get("/retired/").status_code == 404
    assert client.post("/about-us/").status_code == 404


@pytest.mark.django_db
def test_check_redirects_reports_each_address(redirects, tmp_path, capsys):
    sitemap = tmp_path / "page-sitemap.xml"
    sitemap.write_text(
        "<urlset><url><loc>https://distinctive.co.zw/about-us/</loc></url>"
        "<url><loc>https://distinctive.co.zw/services/</loc></url>"
        "<url><loc>https://distinctive.co.zw/jobs/receptionist/</loc></url></urlset>"
    )
    call_command("check_redirects", str(sitemap))
    out = capsys.readouterr().out
    assert "OK       /about-us/ → /about/ (301)" in out
    assert "OK       /services/ (a page here)" in out
    assert "/jobs/receptionist/ → /contact/ (302)" in out
    assert "3 address(es) checked, 0 missing." in out
    assert Redirect.objects.get(old_path="/about-us/").hits == 0  # checking isn't a visit


@pytest.mark.django_db
def test_check_redirects_fails_on_a_missing_address(redirects, tmp_path, capsys):
    urls = tmp_path / "old.txt"
    urls.write_text("# old addresses\n/about-us/\n/2021/08/forgotten-post/\n")
    with pytest.raises(SystemExit) as exit_info:
        call_command("check_redirects", str(urls))
    assert exit_info.value.code == 1
    assert "MISSING  /2021/08/forgotten-post/" in capsys.readouterr().out


@pytest.mark.django_db
def test_check_redirects_lists_the_sitemaps_in_an_index(tmp_path, capsys):
    index = tmp_path / "wp-sitemap.xml"
    index.write_text(
        "<sitemapindex><sitemap><loc>https://distinctive.co.zw/wp-sitemap-posts-post-1.xml</loc>"
        "</sitemap></sitemapindex>"
    )
    call_command("check_redirects", str(index))
    out = capsys.readouterr().out
    assert "is a sitemap index" in out and "wp-sitemap-posts-post-1.xml" in out
