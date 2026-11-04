"""Create the one SiteSettings row, filled with the old site's details, so the admin always has
something to edit. Values are copied here (not imported) so the migration never changes."""

from django.db import migrations


def create_row(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            "company_name": "Distinctive Consultancy Services",
            "tagline": "Bringing excellence into your world.",
            "phone_display": "+263 (24) 2 486 642 - 3",
            "phone_href": "+263242486642",
            "enquiries_email": "enquiries@distinctive.co.zw",
            "recruitment_email": "recruitment@distinctive.co.zw",
            "address": "62 Mutare Road, Beverly, Msasa, Harare",
            "hours": "8:00am – 4:30pm, Monday – Friday",
            "footer_blurb": (
                "If you have any queries or require any of our services, please get hold of us "
                "and we will be happy to serve."
            ),
            "map_query": "62 Mutare Road, Msasa, Harare, Zimbabwe",
        },
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0001_site_settings")]
    operations = [migrations.RunPython(create_row, migrations.RunPython.noop)]
