"""The company's details and links, as shown in the top bar, the footer and the page head.

SiteSettingsService builds a SiteDetails from the admin-edited SiteSettings row, falling back to
DEFAULTS (the old site's values) for anything left empty.
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
    meta_description: str = ""
    og_image_url: str = ""
    ga_measurement_id: str = ""
    map_query: str = ""

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
    meta_description=(
        "Distinctive Consultancy Services, Harare: HR and business consultancy in industrial "
        "relations, HR audits, talent acquisition, people strategy, research surveys and "
        "organisational design."
    ),
    map_query="62 Mutare Road, Msasa, Harare, Zimbabwe",
)
