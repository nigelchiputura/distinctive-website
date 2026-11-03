"""Local development (docker/docker-compose.yml)."""

# django-environ's stubs type every `default=` as NoValue, so these two rules misfire here.
# pyright: reportArgumentType=false, reportAssignmentType=false

from .base import *  # noqa: F403
from .base import env

DEBUG = True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "0.0.0.0"])

# Emails print to the console. Day 7 adds EMAIL_PROVIDER=resend for real sends while testing.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
