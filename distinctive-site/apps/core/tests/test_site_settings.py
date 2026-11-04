"""SiteSettings: one row, defaults for empty fields, and what templates see."""

import pytest
from django.db import IntegrityError
from django.test import override_settings

from apps.core.models import SiteSettings
from apps.core.services.site_details import DEFAULTS
from apps.core.services.site_settings_service import SiteSettingsService


class FakeRepo:
    def __init__(self, row=None):
        self.row = row

    def current(self):
        return self.row


def row(**values):
    """An unsaved SiteSettings with only the given values filled in."""
    return SiteSettings(**values)


def test_no_row_gives_the_defaults():
    assert SiteSettingsService(FakeRepo(None)).get() == DEFAULTS


def test_filled_fields_win_and_empty_ones_fall_back():
    details = SiteSettingsService(
        FakeRepo(row(phone_display="+263 77 000 0000", address="  "))
    ).get()
    assert details.phone_display == "+263 77 000 0000"
    assert details.address == DEFAULTS.address  # whitespace counts as empty
    assert details.enquiries_email == DEFAULTS.enquiries_email


def test_social_links_only_with_urls():
    details = SiteSettingsService(
        FakeRepo(row(linkedin_url="https://linkedin.com/company/distinctive"))
    ).get()
    assert [link.name for link in details.visible_social_links] == ["linkedin"]


@override_settings(GA_MEASUREMENT_ID="G-ENV0000000")
def test_analytics_id_admin_wins_then_environment():
    assert (
        SiteSettingsService(FakeRepo(row(ga_measurement_id="G-ADMIN00000"))).get().ga_measurement_id
        == "G-ADMIN00000"
    )
    assert SiteSettingsService(FakeRepo(row())).get().ga_measurement_id == "G-ENV0000000"
    assert SiteSettingsService(FakeRepo(None)).get().ga_measurement_id == "G-ENV0000000"


@pytest.mark.django_db
def test_the_migration_creates_the_one_row():
    assert SiteSettings.objects.count() == 1
    assert SiteSettings.objects.get().enquiries_email == "enquiries@distinctive.co.zw"


@pytest.mark.django_db
def test_saving_another_row_updates_the_same_one():
    SiteSettings(address="Somewhere else").save()
    assert SiteSettings.objects.count() == 1
    assert SiteSettings.objects.get().address == "Somewhere else"


@pytest.mark.django_db
def test_the_database_refuses_a_second_row():
    with pytest.raises(IntegrityError):
        SiteSettings.objects.bulk_create([SiteSettings(pk=2)])


@pytest.mark.django_db
def test_admin_edits_show_on_the_site(client):
    SiteSettings.objects.filter(pk=1).update(
        phone_display="+263 77 123 4567", facebook_url="https://facebook.com/distinctive"
    )
    html = client.get("/").content.decode()
    assert "+263 77 123 4567" in html
    assert 'href="https://facebook.com/distinctive"' in html
    assert 'aria-label="Social media"' in html


@pytest.mark.django_db
def test_admin_singleton_screens(admin_client):
    listing = admin_client.get("/admin/core/sitesettings/")
    assert listing.status_code == 302 and listing.url.endswith("/admin/core/sitesettings/1/change/")
    assert admin_client.get("/admin/core/sitesettings/1/change/").status_code == 200
    assert admin_client.get("/admin/core/sitesettings/add/").status_code == 403
    assert admin_client.get("/admin/core/sitesettings/1/delete/").status_code == 403
