"""Check that every address of the old site still leads somewhere (docs/deployment.md §8).

    python manage.py check_redirects old-sitemap.xml [more.xml or urls.txt …]

Reads sitemap files (a urlset, or a sitemap index, whose child sitemaps it lists so you can
download them too) or plain text with one address per line. For each address it prints OK and
where it goes (a live page here, or a redirect), or MISSING. Exits with status 1 if anything is
missing, so it can run in a script.
"""

import re
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.urls import Resolver404, resolve

from apps.pages.paths import normalize_path
from apps.pages.services.redirect_service import RedirectService

LOC = re.compile(r"<loc>\s*([^<]+?)\s*</loc>", re.IGNORECASE)


def addresses_in(text: str) -> tuple[list[str], bool]:
    """The addresses in a file, and whether it was a sitemap index (a list of sitemaps)."""
    if "<loc>" in text.lower():
        return LOC.findall(text), "<sitemapindex" in text.lower()
    lines = [line.strip() for line in text.splitlines()]
    return [line for line in lines if line and not line.startswith("#")], False


class Command(BaseCommand):
    help = "Check that each old-site address (from sitemap files) has a page or a redirect."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("files", nargs="+", help="Sitemap XML or text files of old addresses")

    def handle(self, *args: Any, **options: Any) -> None:
        service = RedirectService()
        missing = checked = 0
        for name in options["files"]:
            path = Path(name)
            if not path.is_file():
                raise CommandError(f"No such file: {name}")
            urls, is_index = addresses_in(path.read_text(encoding="utf-8", errors="replace"))
            if is_index:
                self.stdout.write(f"{name} is a sitemap index. Download and check these too:")
                for url in urls:
                    self.stdout.write(f"  {url}")
                continue
            for url in urls:
                checked += 1
                old = normalize_path(url)
                target = service.target_for(old, count=False)
                if target is not None:
                    kind = "301" if target.permanent else "302"
                    self.stdout.write(f"OK       {old} → {target.url} ({kind})")
                    continue
                try:
                    resolve(old)
                except Resolver404:
                    missing += 1
                    self.stdout.write(self.style.ERROR(f"MISSING  {old}"))
                else:
                    self.stdout.write(f"OK       {old} (a page here)")
        summary = f"{checked} address(es) checked, {missing} missing."
        if missing:
            self.stdout.write(self.style.ERROR(summary))
            self.stdout.write("Add a redirect for each in the admin (Redirects), then run again.")
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS(summary))
