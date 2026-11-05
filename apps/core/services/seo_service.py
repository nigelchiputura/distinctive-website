"""What a page tells search engines and social sites (docs/frontend.md §3, `_seo.html`).

Canonical and Open Graph addresses are built from SITE_URL, never from the request's host, so
the preview host and `www` never compete with the live domain. SEO_NOINDEX (the preview host)
adds `noindex` everywhere.
"""

from dataclasses import dataclass, field
from typing import Any

from django.conf import settings
from django.templatetags.static import static

from apps.core.services.base import BaseService
from apps.core.services.site_details import SiteDetails

DEFAULT_IMAGE = "img/og-default.png"  # 1200 × 630
LOCALITY, COUNTRY = "Harare", "ZW"


def absolute_url(path_or_url: str) -> str:
    if path_or_url.startswith(("http://", "https://")):
        return path_or_url
    return settings.SITE_URL.rstrip("/") + "/" + path_or_url.lstrip("/")


@dataclass(frozen=True)
class SeoData:
    title: str
    description: str
    canonical: str
    image: str
    site_name: str
    noindex: bool = False
    og_type: str = "website"
    jsonld: dict[str, Any] | None = field(default=None)


class SeoService(BaseService):
    def __init__(self, site: SiteDetails):
        self.site = site

    def for_page(
        self,
        *,
        path: str,
        title: str,
        meta_title: str = "",
        description: str = "",
        image_url: str = "",
        organization: bool = False,
    ) -> SeoData:
        """`meta_title` is used as written; otherwise "<title> | <company>"."""
        site = self.site
        full_title = meta_title.strip() or f"{title} | {site.company_name}"
        return SeoData(
            title=full_title,
            description=(description.strip() or site.meta_description),
            canonical=absolute_url(path),
            image=absolute_url(image_url or site.og_image_url or static(DEFAULT_IMAGE)),
            site_name=site.company_name,
            noindex=settings.SEO_NOINDEX,
            jsonld=self.organization() if organization else None,
        )

    def organization(self) -> dict[str, Any]:
        """schema.org Organization: the company card Google can show for the name."""
        site = self.site
        street = site.address
        suffix = f", {LOCALITY}"
        if street.endswith(suffix):
            street = street[: -len(suffix)]
        data: dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": site.company_name,
            "url": absolute_url("/"),
            "logo": absolute_url(static("img/logo.png")),
            "email": site.enquiries_email,
            "telephone": site.phone_href,
            "slogan": site.tagline,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": street,
                "addressLocality": LOCALITY,
                "addressCountry": COUNTRY,
            },
        }
        same_as = [link.url for link in site.visible_social_links]
        if same_as:
            data["sameAs"] = same_as
        return data
