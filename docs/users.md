# Users Module

**Project-wide · revised 2026-11-02** (built in Phase 1: the model on Day 1, allauth and the admin
on Day 4; Google redirect URIs for the preview host and the live domain; emails through Resend)

Who logs in: **staff only**. The public site has no accounts and no registration. An admin onboards
each user; users sign in with email + password or with Google. The Django admin (themed with Jazzmin)
is the content-management interface.

## 1. Custom user model

`AbstractUser` (not `AbstractBaseUser`): we keep Django's permission machinery, groups and admin
integration, and adjust fields as needed.

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField("email address", unique=True)
    # Login is by email; username kept (AbstractUser requires it) but auto-filled.
    # Add profile fields here only when needed (display name, job title).

    objects = UserManager()       # apps/users/managers.py

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []          # createsuperuser asks only for the email and password
```

Notes:
- **Set `AUTH_USER_MODEL = "users.User"` before the first migration of any app.** Changing it later is painful. So the `User` model and its `0001` migration are created on **Phase 1 Day 1**, before anything else is migrated; allauth and the admin follow on Day 4.
- Username: `UserManager` (`apps/users/managers.py`, added Phase 1 Day 3) generates it from the email's local part (`tendai.m`, then `tendai.m2` if taken), so admins and `createsuperuser` only type an email. It lives on the manager, not in a service, because Django's own machinery (createsuperuser, the admin, test fixtures) calls `create_user`/`create_superuser` directly.
- Email is lower-cased on save and unique (case-insensitive).
- No `role` field. Roles are Django **Groups** (see §4).

## 2. Layers for the users app

The same pattern as everywhere else, kept small:

| Layer | Contents |
|---|---|
| Model | `User` |
| Repository | `UserRepository(BaseRepository)`: `get_by_email`, `create`, `set_active` |
| Service | `UserService`: `onboard_user(email, first_name, last_name, group)`, `deactivate`, username generation |
| Controller | allauth supplies login/logout/password views; we add none unless needed |
| View | Branded allauth templates in `templates/account/` |
| Adapters | `AccountAdapter`, `SocialAccountAdapter` in `apps/users/adapters.py` — the only custom allauth code |

Admin screens create users directly through the ORM (documented exception); `UserService.onboard_user`
exists for the management command and tests, and keeps one definition of "how a user is onboarded"
(unusable password until they set one, welcome/password-reset email sent).

## 3. allauth configuration

Install `django-allauth` with the Google provider. Check the current allauth docs at install time;
setting names have changed across recent versions. Intended configuration:

```python
INSTALLED_APPS += [
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Email-based login, no self-service sign-up
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]   # irrelevant: signup is closed
ACCOUNT_EMAIL_VERIFICATION = "optional"       # admins pre-create verified users
ACCOUNT_ADAPTER = "apps.users.adapters.AccountAdapter"
SOCIALACCOUNT_ADAPTER = "apps.users.adapters.SocialAccountAdapter"

# Google: only an EXISTING user may sign in; match by verified email
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_PROVIDERS = {
    "google": {"SCOPE": ["profile", "email"], "AUTH_PARAMS": {"access_type": "online"}},
}
LOGIN_REDIRECT_URL = "/admin/"       # or the env-driven admin path
LOGOUT_REDIRECT_URL = "/"
```

```python
# apps/users/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False                     # no public registration

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return False                     # Google can log in existing users, never create new ones
```

**Google sign-in behaviour:** a Google account whose verified email matches an existing active user
is connected and logged in; any other Google account is refused with a friendly message. There is
**no domain restriction** (decided 2026-10-08); if one is ever wanted, the adapter is where that
check would live.

Google Cloud setup: OAuth client (Web), authorised redirect URIs per host:
`http://localhost:8000/accounts/google/login/callback/`,
`https://new.distinctive.co.zw/accounts/google/login/callback/` (the preview host) and
`https://distinctive.co.zw/accounts/google/login/callback/` (live). Register all three on Phase 1
Day 4 so the cutover needs no Google change.
Credentials go in `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` env vars (not committed).

## 4. Roles and permissions

Roles are not a concern this phase. Minimal, extensible setup:

| Group | Permissions | Created by |
|---|---|---|
| **Superuser** | Everything | `createsuperuser` |
| **Content Editor** | Add/change/delete pages, sections, slides, services, team, partners, redirects; change site settings; view and mark contact submissions; **no** user management. Phase 2 adds jobs (a further data migration) | Data migration in `users` |

Staff users need `is_staff=True` to reach the admin. A user with no group sees nothing.

## 5. Admin (Jazzmin)

```python
INSTALLED_APPS = ["jazzmin", ...]       # before django.contrib.admin
JAZZMIN_SETTINGS = {
    "site_title": "Distinctive Admin",
    "site_header": "Distinctive",
    "site_brand": "Distinctive",
    "site_logo": "img/logo.png",
    "welcome_sign": "Sign in to manage the website",
    "copyright": "Distinctive Consultancy Services",
    "search_model": ["offerings.Service", "team.TeamMember"],      # Phase 2 adds jobs.JobPosting
    "order_with_respect_to": ["pages", "offerings", "team", "contact", "core", "users"],
    "icons": {"team.TeamMember": "fas fa-users", "contact.ContactSubmission": "fas fa-envelope"},
    "show_ui_builder": False,
}
JAZZMIN_UI_TWEAKS = {"navbar": "navbar-dark", "accent": "accent-warning"}   # gold-ish accent
```

Admin ergonomics that matter to this project:
- Page admin with **inline** sections and slides, drag-to-reorder via `sort_order`.
- Contact submissions: read-only fields, `email_sent` / `handled` / `source_page` filters, "Mark as handled" and "Resend notification email" actions.
- Site settings: a single row, no add or delete once it exists.
- Redirects: old path, new path, hit count (so unused ones can be pruned later).
- Phase 2: the job admin with the EasyMDE Markdown editor (vendored), filters for department / employment type / open vs closed, closing date in `list_display`.
- Image fields with preview thumbnails; `alt_text` fields required for meaningful images.
- Admin served at an env-driven path (`ADMIN_URL_PATH`), not `/admin/`, in production.

## 6. Security checklist

- Password validators on; minimum length 12.
- allauth login rate limiting on; admin path not guessable; `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT` in production settings.
- Deactivate rather than delete leaving users.
- No user data is exposed in templates; search index never contains user data.
- 2FA is deferred (backlog).

## 7. Onboarding flow

1. Superuser opens Admin → Users → Add: email, name, group, `is_staff` ticked.
2. User receives a set-password email, sent through Resend (`deployment.md` §6), or just uses Google if their Google email matches. Before Resend is verified, run `onboard_user` and give the user a password reset link from the console output instead.
3. User signs in at the admin path; sees only the sections their group allows.

## 8. Tests (`Phase_1/Test_Plan.md` §3.5)

- `is_open_for_signup` returns False for both adapters; the signup URL returns 404/redirect.
- Google login: existing email → logged in; unknown email → refused; inactive user → refused.
- `UserService.onboard_user` generates unique usernames and lower-cases emails.
- Content Editor group cannot access user management.
