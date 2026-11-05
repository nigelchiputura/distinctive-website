"""Settings shared by every environment. dev.py, test.py and prod.py import from here.

Values that differ per environment come from environment variables (see .env.example and
docs/deployment.md §3). Nothing secret is committed.
"""

# django-environ's stubs type every `default=` as NoValue, so these two rules misfire here.
# pyright: reportArgumentType=false, reportAssignmentType=false

from pathlib import Path

import environ

from .email import email_settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
# Locally, read .env from the repo root. In containers the variables are already set
# (compose's env_file, or the VPS .env), so a missing file is fine.
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

SECRET_KEY = env("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS: list[str] = env.list("CSRF_TRUSTED_ORIGINS", default=[])
SITE_URL: str = env("SITE_URL", default="http://localhost:8000")

# Where the admin lives. Not guessable in production (docs/users.md §5).
ADMIN_URL_PATH: str = env("ADMIN_URL_PATH", default="admin/")

INSTALLED_APPS = [
    "jazzmin",  # the admin theme; must come before django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "anymail",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # Project apps. Phase 2 adds apps.jobs and apps.search.
    "apps.core",
    "apps.users",
    "apps.pages",
    "apps.offerings",
    "apps.team",
    "apps.contact",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site",
            ],
        },
    },
]

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

# The custom user model exists from the first migration (docs/users.md §1).
AUTH_USER_MODEL = "users.User"

# ---- Sign-in: django-allauth (docs/users.md §3) ----------------------------------------------
# Staff only. No public sign-up; admins onboard users; Google signs in existing users only.
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
ACCOUNT_ADAPTER = "apps.users.adapters.AccountAdapter"
SOCIALACCOUNT_ADAPTER = "apps.users.adapters.SocialAccountAdapter"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]  # unused: sign-up is closed
ACCOUNT_EMAIL_VERIFICATION = "none"  # admins create the accounts; nothing to verify
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Distinctive website] "
ACCOUNT_SESSION_REMEMBER = None  # "Remember me" box on the sign-in form
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_USER_DISPLAY = "apps.users.display.user_display"
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_LOGIN_ON_GET = False  # the Google button POSTs (CSRF-protected)

GOOGLE_CLIENT_ID: str = env("GOOGLE_CLIENT_ID", default="")
GOOGLE_CLIENT_SECRET: str = env("GOOGLE_CLIENT_SECRET", default="")
GOOGLE_LOGIN_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online", "prompt": "select_account"},
        "APPS": (
            [{"client_id": GOOGLE_CLIENT_ID, "secret": GOOGLE_CLIENT_SECRET, "key": ""}]
            if GOOGLE_LOGIN_ENABLED
            else []
        ),
    }
}

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/" + ADMIN_URL_PATH
LOGOUT_REDIRECT_URL = "/"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Africa/Harare"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email: EMAIL_PROVIDER picks the backend (config/settings/email.py, docs/deployment.md §6).
# Locally it prints emails; set EMAIL_PROVIDER=resend in .env to send for real.
globals().update(email_settings(env, default_provider="console"))

# The admin theme (docs/users.md §5).
JAZZMIN_SETTINGS = {
    "site_title": "Distinctive Admin",
    "site_header": "Distinctive",
    "site_brand": "Distinctive",
    "site_logo": "img/logo.png",
    "site_logo_classes": "",
    "login_logo": "img/logo.png",
    "site_icon": None,
    "welcome_sign": "Sign in to manage the website",
    "copyright": "Distinctive Consultancy Services",
    "search_model": ["users.User"],  # Days 5–6 add services and team members
    "user_avatar": None,
    "topmenu_links": [
        {"name": "View website", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["contact", "pages", "offerings", "team", "core", "users", "auth"],
    "icons": {
        "core.SiteSettings": "fas fa-sliders-h",
        "pages.Page": "fas fa-file-alt",
        "offerings.Service": "fas fa-briefcase",
        "pages.Partner": "fas fa-handshake",
        "team.TeamMember": "fas fa-user-tie",
        "contact.ContactSubmission": "fas fa-inbox",
        "users.User": "fas fa-user",
        "auth.Group": "fas fa-users-cog",
        "account.EmailAddress": "fas fa-at",
        "socialaccount.SocialAccount": "fab fa-google",
        "socialaccount.SocialApp": "fas fa-key",
        "socialaccount.SocialToken": "fas fa-ticket-alt",
        "sites.Site": "fas fa-globe",
    },
    "hide_apps": ["sites", "socialaccount", "account"],
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "related_modal_active": False,
    "custom_css": "css/admin.css",  # compiled from static/scss/admin.scss
    "use_google_fonts_cdn": False,  # no third-party requests, in the admin too
}
JAZZMIN_UI_TWEAKS = {
    "theme": "default",
    "navbar": "navbar-white navbar-light",
    "sidebar": "sidebar-dark-warning",
    "accent": "accent-warning",
    "brand_colour": False,  # static/scss/admin.scss puts the logo on white
    "button_classes": {
        "primary": "btn-warning",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

# Google Analytics 4. The admin's SiteSettings value wins; this is the fallback.
GA_MEASUREMENT_ID: str = env("GA_MEASUREMENT_ID", default="")

# Warnings and errors go to the container output. Without this, Django logs almost nothing
# with DEBUG off (lesson from Consult 360; docs/deployment.md §6).
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {"format": "{levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "plain"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
