"""manage.py seed_site_content: load the old site's content (apps/core/seed/content.py).

Adds only what's missing and never changes what's there. The entrypoint runs it when
SEED_SITE_CONTENT=true (first deploy only, docs/deployment.md §2.1).
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.services.seed_service import SeedService


class Command(BaseCommand):
    help = "Load the old site's content. Adds only what is missing; safe to run again."

    def handle(self, *args, **options) -> None:
        with transaction.atomic():
            report = SeedService().seed()
        if not report.total:
            self.stdout.write("Nothing to add: the content is already there.")
            return
        added = ", ".join(
            f"{n} {kind if n != 1 else kind.removesuffix('s')}"
            for kind, n in report.created.items()
        )
        self.stdout.write(self.style.SUCCESS(f"Added {added}."))
