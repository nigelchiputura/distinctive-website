"""The company's contact details and links, as shown in the top bar and the footer.

Day 2 uses DEFAULTS, the values on the old site. Day 3 adds the SiteSettings model, editable in
the admin, and SiteSettingsService falls back to these same DEFAULTS for anything left empty.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SocialLink:
    name: str  # "facebook" | "linkedin" | "instagram" | "x": also the icon's file name
    label: str
    url: str


@dataclass(frozen=True)
class SiteDetails:
    company_name: str
    tagline: str
    phone_display: str
    phone_href: str
    enquiries_email: str
    recruitment_email: str
    address: str
    hours: str
    footer_blurb: str
    social_links: tuple[SocialLink, ...] = field(default_factory=tuple)

    @property
    def visible_social_links(self) -> tuple[SocialLink, ...]:
        """Only links with a URL: an empty URL hides its icon (Phase 1 Scope D13)."""
        return tuple(link for link in self.social_links if link.url)


# From the old site (footer and top bar screenshots, 2026-10-06). Social URLs are empty until
# the client confirms them, so no icon shows yet.
DEFAULTS = SiteDetails(
    company_name="Distinctive Consultancy Services",
    tagline="Bringing excellence into your world.",
    phone_display="+263 (24) 2 486 642 - 3",
    phone_href="+263242486642",
    enquiries_email="enquiries@distinctive.co.zw",
    recruitment_email="recruitment@distinctive.co.zw",
    address="62 Mutare Road, Beverly, Msasa, Harare",
    hours="8:00am – 4:30pm, Monday – Friday",
    footer_blurb=(
        "If you have any queries or require any of our services, please get hold of us and we "
        "will be happy to serve."
    ),
    social_links=(
        SocialLink("facebook", "Facebook", ""),
        SocialLink("linkedin", "LinkedIn", ""),
        SocialLink("instagram", "Instagram", ""),
        SocialLink("x", "X (Twitter)", ""),
    ),
)
