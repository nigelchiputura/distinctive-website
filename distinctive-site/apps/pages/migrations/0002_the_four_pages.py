"""The site's four Phase 1 pages, so every URL works on a fresh database. Their content comes
from the admin or `manage.py seed_site_content`."""

from django.db import migrations

PAGES = (
    ("home", "Home"),
    ("about", "About Us"),
    ("services", "Services"),
    ("contact", "Contact Us"),
)


def create_pages(apps, schema_editor):
    Page = apps.get_model("pages", "Page")
    for slug, title in PAGES:
        Page.objects.get_or_create(slug=slug, defaults={"title": title, "is_published": True})


class Migration(migrations.Migration):
    dependencies = [("pages", "0001_initial")]

    operations = [migrations.RunPython(create_pages, migrations.RunPython.noop)]
