"""Static file storage for production (config/settings/prod.py).

WhiteNoise's manifest storage gives every static file a hashed name and refuses any name that
isn't in its manifest. That refusal is useful: a template pointing at a missing file fails loudly
instead of shipping a broken link. But Jazzmin 3's admin/base.html asks for the URL of a
*folder*, `{% static 'vendor/bootswatch' %}` (the base its theme chooser builds theme addresses
from), and folders are never in the manifest, so every admin page answered 500 in production
(docs/errors-and-exceptions/jazzmin-bootswatch-folder-breaks-admin-in-prod__2026-11-09_1606/).
"""

from whitenoise.storage import CompressedManifestStaticFilesStorage


class StaticStorage(CompressedManifestStaticFilesStorage):
    """The manifest storage, with a named list of folders that are passed through unhashed.

    Only these exact names are let through; any other name missing from the manifest still
    raises, so a real missing file is still caught.
    """

    UNHASHED_FOLDERS: frozenset[str] = frozenset({"vendor/bootswatch"})

    def stored_name(self, name: str) -> str:
        if name.strip("/") in self.UNHASHED_FOLDERS:
            return name
        return super().stored_name(name)
