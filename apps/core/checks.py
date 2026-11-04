"""Start-up warnings for email settings that would fail quietly (docs/deployment.md §6).

They run with every management command, including the entrypoint's `migrate`, so they land in
the container logs. Learned on Consult 360, where a demo sent from noreply@localhost for days.
"""

from email.utils import parseaddr

from django.conf import settings
from django.core.checks import CheckMessage, Warning, register

_NOT_REAL_DOMAINS = ("localhost", ".localhost", ".local", ".test", ".invalid")


def _domain(address: str) -> str:
    return parseaddr(address)[1].rpartition("@")[2].lower()


def _is_real_domain(domain: str) -> bool:
    if not domain or "." not in domain:
        return False
    if domain.startswith("example.") or ".example." in domain or domain == "example":
        return False
    return not any(domain == d.lstrip(".") or domain.endswith(d) for d in _NOT_REAL_DOMAINS)


@register()
def email_settings_check(app_configs=None, **kwargs) -> list[CheckMessage]:
    provider = getattr(settings, "EMAIL_PROVIDER", "console")
    if provider == "console":
        return []  # nothing is really sent, so nothing can silently fail

    messages: list[CheckMessage] = []
    sender = getattr(settings, "DEFAULT_FROM_EMAIL", "")
    if not _is_real_domain(_domain(sender)):
        messages.append(
            Warning(
                f"DEFAULT_FROM_EMAIL {sender!r} isn't on a real domain, so the email provider "
                "will refuse every message.",
                hint="Set DEFAULT_FROM_EMAIL to an address on the verified sending domain, e.g. "
                "'Distinctive Website <website@mail.distinctive.co.zw>'.",
                id="core.W001",
            )
        )
    if provider == "resend" and not settings.ANYMAIL.get("RESEND_API_KEY"):
        messages.append(
            Warning(
                "EMAIL_PROVIDER is 'resend' but RESEND_API_KEY is empty, so no email can be sent.",
                hint="Set RESEND_API_KEY to a Sending-access key for the sending domain.",
                id="core.W002",
            )
        )
    if provider == "smtp" and not (settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD):
        messages.append(
            Warning(
                "EMAIL_PROVIDER is 'smtp' but EMAIL_HOST_USER or EMAIL_HOST_PASSWORD is empty.",
                hint="Set the SMTP login, or use EMAIL_PROVIDER=resend.",
                id="core.W003",
            )
        )
    return messages
