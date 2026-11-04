"""pytest (pytest.ini) and CI. Uses Postgres, like production (docs/Testing_Strategy.md §2)."""

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]

# The default hasher is deliberately slow; tests that create users would crawl
# (a lesson logged on Consult 360).
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_PROVIDER = "console"  # no start-up email checks in tests (they're tested directly)
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Per-process memory, cleared before each test (conftest.py), so rate-limit tests start at zero.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
GOOGLE_MAPS_EMBED_KEY = "test-maps-key"
GA_MEASUREMENT_ID = ""
