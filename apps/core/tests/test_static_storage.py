"""The production static storage (apps/core/storage.py).

Tests normally use Django's plain storage, which never checks that a file exists, so a template
asking for a missing static file only fails in production. That is how every admin page came to
answer 500 on the demo host (Jazzmin asks for a folder). These tests use the production storage.
"""

import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import override_settings

from apps.core.storage import StaticStorage


def _storage_with(hashed_files: dict[str, str]) -> StaticStorage:
    storage = StaticStorage()
    storage.hashed_files = hashed_files
    return storage


def test_jazzmins_folder_is_passed_through_unhashed():
    storage = _storage_with({})
    assert storage.url("vendor/bootswatch", force=True) == "/static/vendor/bootswatch"


def test_a_real_file_still_gets_its_hashed_name():
    storage = _storage_with({"css/main.css": "css/main.abc123.css"})
    assert storage.url("css/main.css", force=True) == "/static/css/main.abc123.css"


def test_any_other_missing_name_still_fails_loudly():
    storage = _storage_with({})
    with pytest.raises(ValueError, match="Missing staticfiles manifest entry"):
        storage.url("css/no-such-file.css", force=True)


@pytest.mark.django_db
def test_the_admin_renders_with_the_production_storage(admin_client, tmp_path):
    """collectstatic into a scratch folder, then open the admin as production would."""
    storages = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "apps.core.storage.StaticStorage"},
    }
    with override_settings(STATIC_ROOT=tmp_path, STORAGES=storages):
        call_command("collectstatic", interactive=False, verbosity=0)
        response = admin_client.get("/" + settings.ADMIN_URL_PATH)
    assert response.status_code == 200
    assert 'data-theme-base="/static/vendor/bootswatch"' in response.content.decode()
