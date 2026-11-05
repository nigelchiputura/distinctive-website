"""Name the django.contrib.sites row that allauth uses in its emails (it defaults to
example.com). The domain is the live one; links in emails are built from the request or
SITE_URL, so the preview host and localhost still work."""

from django.db import migrations


def name_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    Site.objects.update_or_create(
        pk=1, defaults={"domain": "distinctive.co.zw", "name": "Distinctive Consultancy Services"}
    )


class Migration(migrations.Migration):
    dependencies = [("users", "0002_email_login_manager"), ("sites", "0002_alter_domain_unique")]
    operations = [migrations.RunPython(name_site, migrations.RunPython.noop)]
