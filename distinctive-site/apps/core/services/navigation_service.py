"""The site's navigation: one ordered list used by the navbar and the footer.

Phase 2 adds Jobs here (and the search icon in the navbar), so adding a page is one entry.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class NavItem:
    label: str
    url: str
    active: bool = False


# Phase 1 pages (docs/Phase_1/Phase1_Scope.md D11). Paths, not URL names, because the pages
# themselves arrive on Days 5–8; they switch to reversed URL names then.
PHASE_1_ITEMS: tuple[tuple[str, str], ...] = (
    ("Home", "/"),
    ("About Us", "/about/"),
    ("Services", "/services/"),
    ("Contact Us", "/contact/"),
)


class NavigationService:
    def __init__(self, items: tuple[tuple[str, str], ...] = PHASE_1_ITEMS):
        self.items = items

    def items_for(self, current_path: str) -> list[NavItem]:
        """The nav items, with the one for the current page marked active.

        Home is active only on "/" itself; other items are active on their own path and
        anything below it (so /services/#hr-audits or a later /about/team/ still marks theirs).
        """
        return [
            NavItem(label, url, self._is_active(url, current_path)) for label, url in self.items
        ]

    @staticmethod
    def _is_active(url: str, current_path: str) -> bool:
        if url == "/":
            return current_path == "/"
        return current_path == url or current_path.startswith(url)
