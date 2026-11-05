"""Production settings (Test Plan §3.7)."""

import os
import subprocess
import sys

from django.conf import settings


def test_check_deploy_with_prod_settings_has_only_the_two_silenced_warnings():
    env = {
        **os.environ,
        "DJANGO_SETTINGS_MODULE": "config.settings.prod",
        "SECRET_KEY": "x" * 60 + "-not-a-real-key-but-long-and-varied-1234567890",
        "ALLOWED_HOSTS": "distinctive.co.zw",
        "EMAIL_PROVIDER": "console",
    }
    result = subprocess.run(
        [sys.executable, "manage.py", "check", "--deploy", "--fail-level", "WARNING"],
        cwd=settings.BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "System check identified no issues (2 silenced)." in result.stdout


def test_prod_settings_values():
    code = (
        "from django.conf import settings as s;"
        "print(s.DEBUG, s.SESSION_COOKIE_SECURE, s.CSRF_COOKIE_SECURE, s.SECURE_SSL_REDIRECT,"
        " s.SECURE_HSTS_SECONDS > 0, s.X_FRAME_OPTIONS, s.SECURE_CONTENT_TYPE_NOSNIFF,"
        " s.SECURE_REFERRER_POLICY, s.TRUSTED_PROXY_COUNT, s.SILENCED_SYSTEM_CHECKS)"
    )
    env = {
        **os.environ,
        "DJANGO_SETTINGS_MODULE": "config.settings.prod",
        "EMAIL_PROVIDER": "console",
    }
    result = subprocess.run(
        [sys.executable, "-c", f"import django; django.setup(); {code}"],
        cwd=settings.BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == [
        "False", "True", "True", "True", "True", "DENY", "True",
        "strict-origin-when-cross-origin", "1", "['security.W005',", "'security.W021']",
    ]  # fmt: skip
