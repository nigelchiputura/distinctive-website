"""SiteDetails and its defaults."""

from apps.core.services.site_details import DEFAULTS, SiteDetails, SocialLink


def test_defaults_are_the_old_sites_details():
    assert DEFAULTS.enquiries_email == "enquiries@distinctive.co.zw"
    assert DEFAULTS.phone_display == "+263 (24) 2 486 642 - 3"
    assert "62 Mutare Road" in DEFAULTS.address


def test_empty_social_urls_are_hidden():
    details = SiteDetails(
        **{
            **DEFAULTS.__dict__,
            "social_links": (
                SocialLink("facebook", "Facebook", "https://facebook.com/distinctive"),
                SocialLink("x", "X (Twitter)", ""),
            ),
        }
    )
    assert [link.name for link in details.visible_social_links] == ["facebook"]


def test_no_social_icons_until_urls_are_confirmed():
    assert DEFAULTS.visible_social_links == ()
