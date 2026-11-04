"""manage.py seed_site_content: load the old site's content (apps/core/seed/content.py).

Adds what's missing and fills in fields that are still empty; never changes what an editor has
filled in. The entrypoint runs it when
SEED_SITE_CONTENT=true (first deploy only, docs/deployment.md §2.1).
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.services.seed_service import SeedService


class Command(BaseCommand):
    help = "Load the old site's content. Adds what's missing, fills empty fields; safe to re-run."

    def handle(self, *args, **options) -> None:
        with transaction.atomic():
            report = SeedService().seed()
        if not report.total:
            self.stdout.write("Nothing to add: the content is already there.")
            return
        created = dict(report.created)
        filled = created.pop("filled in", 0)
        added = ", ".join(
            f"{n} {kind if n != 1 else kind.removesuffix('s')}" for kind, n in created.items()
        )
        lines = []
        if added:
            lines.append(f"Added {added}.")
        if filled:
            lines.append(f"Filled in empty fields on {filled} existing item(s).")
        self.stdout.write(self.style.SUCCESS(" ".join(lines)))
