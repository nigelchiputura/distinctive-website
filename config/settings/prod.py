"""Production: the VPS (docker/docker-compose.prod.yml), and the image build's collectstatic."""

from .base import *  # noqa: F403
from .base import MIDDLEWARE, env

DEBUG = False

# WhiteNoise serves static files from inside the container, right after SecurityMiddleware.
MIDDLEWARE = [MIDDLEWARE[0], "whitenoise.middleware.WhiteNoiseMiddleware", *MIDDLEWARE[1:]]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Caddy terminates TLS and forwards the scheme (docs/deployment.md §7).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
# Not HttpOnly: static/js/modules/http.js reads it for the X-CSRFToken header.
CSRF_COOKIE_HTTPONLY = False
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
# One week to start; raise to a year once the domain has been stable (docs/deployment.md §7).
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=604800)
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
# Deliberate, so silenced (docs/deployment.md §7): other distinctive.co.zw subdomains (mail,
# webmail on the old host) aren't ours to force onto HTTPS, and preload is hard to undo.
SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]
