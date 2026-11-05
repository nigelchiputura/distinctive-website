"""Email settings, chosen by EMAIL_PROVIDER (docs/deployment.md §6).

    console  prints emails (local default)
    resend   Resend's HTTPS API through django-anymail (production default)
    smtp     any SMTP relay (a fallback; many VPS providers block SMTP ports)

base.py calls this with "console"; prod.py calls it again with "resend" as the default.
"""

from typing import Any

import environ
from django.core.exceptions import ImproperlyConfigured

BACKENDS = {
    "console": "django.core.mail.backends.console.EmailBackend",
    "resend": "anymail.backends.resend.EmailBackend",
    "smtp": "django.core.mail.backends.smtp.EmailBackend",
}


def email_settings(env: environ.Env, default_provider: str) -> dict[str, Any]:
    provider = env.str("EMAIL_PROVIDER", default=default_provider).strip().lower()
    if provider not in BACKENDS:
        raise ImproperlyConfigured(
            f"EMAIL_PROVIDER={provider!r} isn't one of: {', '.join(sorted(BACKENDS))}."
        )
    sender = env.str(
        "DEFAULT_FROM_EMAIL", default="Distinctive Website <website@website.localhost>"
    )
    return {
        "EMAIL_PROVIDER": provider,
        "EMAIL_BACKEND": BACKENDS[provider],
        "DEFAULT_FROM_EMAIL": sender,
        "SERVER_EMAIL": sender,
        "CONTACT_RECIPIENT": env.str("CONTACT_RECIPIENT", default="enquiries@distinctive.co.zw"),
        "ANYMAIL": {
            "RESEND_API_KEY": env.str("RESEND_API_KEY", default=""),
            "REQUESTS_TIMEOUT": 20,
        },
        "EMAIL_HOST": env.str("EMAIL_HOST", default=""),
        "EMAIL_PORT": env.int("EMAIL_PORT", default=587),
        "EMAIL_USE_TLS": env.bool("EMAIL_USE_TLS", default=True),
        "EMAIL_HOST_USER": env.str("EMAIL_HOST_USER", default=""),
        "EMAIL_HOST_PASSWORD": env.str("EMAIL_HOST_PASSWORD", default=""),
        "EMAIL_TIMEOUT": 20,
    }
