"""Each fixed page's URL name, by its slug: for canonical addresses and the sitemap."""

from django.urls import NoReverseMatch, reverse

PAGE_URL_NAMES: dict[str, str] = {
    "home": "pages:home",
    "about": "pages:about",
    "services": "pages:services",
    "contact": "contact:contact",
}


def page_path(slug: str) -> str | None:
    """'/about/' for "about"; None for a page the site has no URL for."""
    name = PAGE_URL_NAMES.get(slug)
    if name is None:
        return None
    try:
        return reverse(name)
    except NoReverseMatch:
        return None
