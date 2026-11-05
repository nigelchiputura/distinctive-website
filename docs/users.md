# Users Module

**Project-wide · as built on Phase 1 Day 4 (2026-11-03)**: the model on Day 1, the email-login
manager on Day 3, allauth, onboarding, the Content Editor group and the Jazzmin admin on Day 4.

Who signs in: **staff only**. The public site has no accounts and no registration. An admin
onboards each user; users sign in with email and password, or with Google if their Google
account has the same address. The Django admin, themed with Jazzmin, is where content is managed.

## 1. Custom user model

`AbstractUser` (not `AbstractBaseUser`): we keep Django's permissions, groups and admin
integration.

```python
# apps/users/models.py
class User(AbstractUser):
    email = models.EmailField("email address", unique=True)

    objects = UserManager()       # apps/users/managers.py

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []          # createsuperuser asks only for the email and password
```

- **`AUTH_USER_MODEL = "users.User"` came before any other migration** (Phase 1 Day 1).
- **Username:** `UserManager.username_for` makes it from the email's local part (`tendai.m`, then
  `tendai.m2` if taken). It lives on the manager because Django's own machinery
  (`createsuperuser`, the admin, test fixtures) calls `create_user`/`create_superuser` directly.
  Users never see it: allauth's messages name people by email (`ACCOUNT_USER_DISPLAY`).
- Email is lower-cased and trimmed on save, and unique.
- No `role` field: roles are Django groups (§4).

## 2. Layers

| Layer | Contents |
|---|---|
| Model | `User`, `UserManager` |
| Repository | `UserRepository`: `get_by_email` (case-insensitive), `create_user`, `set_active`, `add_to_group`, `set_group_permissions` |
| Service | `UserService`: `onboard_user`, `welcome` (set-password link + email), `set_password_link`, `active_user_for_email`, `deactivate`, `sync_content_editor_group`. The repository, the mailer and the token maker are injected, so its tests need no database |
| Controller | allauth's views (sign in, sign out, password reset); none of our own |
| View | `templates/allauth/layouts/base.html` (every allauth page in the site's layout, in a card), `templates/account/login.html`, `password_reset_from_key.html`, `password_reset_from_key_done.html` |
| Adapters | `AccountAdapter`, `SocialAccountAdapter` in `apps/users/adapters.py`: the only custom allauth code |
| Command | `manage.py onboard_user EMAIL [--first] [--last] [--group] [--no-email]` |

## 3. allauth

`django-allauth[socialaccount]` 65.x. Settings in `config/settings/base.py`:

- `ACCOUNT_LOGIN_METHODS = {"email"}`; `ACCOUNT_EMAIL_VERIFICATION = "none"` (admins create the
  accounts, so there is nothing to verify); "Keep me signed in" box on the form.
- **Sign-up is closed** in both adapters. `/accounts/signup/` shows "Sign Up Closed" and a POST
  creates nothing.
- **One sign-in page.** The admin's own login URL redirects to `/accounts/login/` (keeping
  `?next=`), so Google sign-in and allauth's rate limiting on failed attempts apply to the admin
  too. After signing in, people land in the admin (`LOGIN_REDIRECT_URL`).
- The sign-in page is our own: allauth's default tells visitors to "sign up first".
- **Set-password page:** a new user's link and a forgotten-password link both land on
  "Set your password". An used or expired link says so and offers a new one.

**Google** (`SocialAccountAdapter.pre_social_login`): once Google answers,

- an already-connected Google account signs in, unless its user has been deactivated;
- otherwise the Google account's **verified** email is matched to an **active** staff user
  (case-insensitive) and connected on first use;
- anything else (no such user, an unverified email, a deactivated user) is refused with "That
  Google account isn't linked to a staff account on this website…" on the sign-in page. Nobody is
  ever created.

There is no domain restriction (decided 2026-10-08).

The button appears only when `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set (the provider
app is configured from them in settings; nothing to add in the admin). It POSTs, with CSRF
(`SOCIALACCOUNT_LOGIN_ON_GET = False`), and asks Google to show the account chooser.

**Google Cloud setup (owner):** an OAuth client of type *Web application* with these authorised
redirect URIs, all three now so the cutover needs no Google change:

- `http://localhost:8000/accounts/google/login/callback/`
- `https://new.distinctive.co.zw/accounts/google/login/callback/` (the preview host)
- `https://distinctive.co.zw/accounts/google/login/callback/` (live)

The OAuth consent screen needs the app name, a support email and the `email` and `profile`
scopes. Put the client ID and secret in `.env` (never committed).

`django.contrib.sites` is named "Distinctive Consultancy Services" by a migration
(`users.0003_site_name`), because allauth uses it in its emails.

**Template context:** allauth's views put that `Site` record into the context as `site`. The
site's own details are therefore `site_info` (see `errors-and-exceptions/allauth-site-context-hid-site-details__2026-11-03_1120/`).

## 4. Roles and permissions

| Group | Permissions | How |
|---|---|---|
| **Superuser** | Everything | `createsuperuser` |
| **Content Editor** | Add, change, delete and view pages, sections, slides, partners, redirects, services and team members; change site settings; view and change (mark handled, resend) contact submissions. **No** users, groups or sign-in records | `apps/users/permissions.py` |

`UserService.sync_content_editor_group` gives the group **exactly** that list. It runs after
every `migrate` (a `post_migrate` handler in `UsersConfig.ready`), so a model added on a later day
gets its permissions the moment its migration runs; nothing else needs updating. Phase 2 adds the
jobs model to the list.

Staff users need `is_staff` to reach the admin. Someone with no group sees an empty admin.

## 5. Admin (Jazzmin)

`django-jazzmin` 3.x, configured in `config/settings/base.py` (`JAZZMIN_SETTINGS`,
`JAZZMIN_UI_TWEAKS`):

- title "Distinctive Admin", the logo on a white strip at the top of the sidebar, gold accent,
  "View website" in the top bar;
- the Sites, social-account and email-address tables are hidden (nothing for an editor to do
  there);
- `custom_css: css/admin.css`, compiled by `npm run build:css` from `static/scss/admin.scss` with
  the site's tokens (`frontend.md` §1);
- `use_google_fonts_cdn: False`: no third-party requests in the admin either.

**Users screen:**

- **Add user** asks for an email, a name and groups (Content Editor ticked by default). No
  password: the user gets none, is made staff, and is emailed a set-password link. If the email
  can't be sent, the link is shown on screen to pass on.
- Actions: **Deactivate** (never yourself) and **Email a new set-password link**.
- The change screen shows the username and dates as read-only.

**Site settings** (Day 3): a single row, no add or delete.

**Pages** (Day 5): the four fixed pages; no add or delete. Each opens in tabs: General, Search
engines, then **Hero slides** (Home only) and **Sections**, edited inline with a thumbnail of the
current image. A section's "order" number sets its place on the page; unticking "published" hides
it without deleting it.

**Services** (Day 5): the list shows a thumbnail and lets an editor change "show on Home", the
order and "published" right in the list.

**Team members** and **Partners and clients** (Day 6): lists with a thumbnail and the order and
"published" editable in place; partners filter by kind. Typing `linkedin.com/in/…` without
`https://` is accepted.

**Enquiries** (Day 7; first in the menu): read-only, newest first, filtered by "email sent",
"handled" and "sent from", searchable, with a date bar. Actions: **Mark as handled** and **Resend
notification email** (which reports how many were sent and how many still failed; the provider's
message is on each enquiry). Nobody can add an enquiry in the admin; a Content Editor can't delete
one. A Service has a new tick box, "show the image on the Services page".

**Forms and the map as sections** (Day 8): the Contact page's form and map, and the gold enquiry
block on Services, are sections like any other ("Contact form beside “Reach Us”", "Enquiry form
on gold", "Map"). An editor can change their headings, the text under them and the button label,
reorder or unpublish them. The address, phone, email, hours and vacancies address they show come
from **Site settings**, so they're edited once for the whole site. Enquiries from Services show
"sent from: Services page".

Later days add: redirects (Day 9) and Phase 2's job admin.

The admin lives at `ADMIN_URL_PATH` (`admin/` locally; something not guessable in production).

## 6. Security checklist

- Password validators on; minimum length 12.
- allauth's rate limits on failed sign-ins; the admin path not guessable in production;
  secure session and CSRF cookies, HTTPS redirect and HSTS in production settings.
- The Google button posts with CSRF; only verified Google emails are matched.
- Leavers are deactivated, never deleted.
- Set-password links work once and expire after `PASSWORD_RESET_TIMEOUT` (3 days).
- No user data in public templates; Phase 2's search index never contains user data.
- 2FA is in the backlog.

## 7. Onboarding

1. **Admin → Users → Add user**: email, name, groups. Or on the server:
   `python manage.py onboard_user rudo.moyo@distinctive.co.zw --first Rudo --last Moyo`.
2. They receive "Your Distinctive website account" with a set-password link (through Resend,
   `deployment.md` §6). Before Resend is verified, use `--no-email` (or the admin's on-screen link)
   and pass the link on yourself.
3. They set a password, sign in at `/accounts/login/` (or with Google, if configured), and see only
   what their group allows.

## 8. Tests

`apps/users/tests/`: `test_user_service.py` (fakes, no database), `test_adapters.py` (the Google
rules), `test_sign_in.py` (sign in, sign up closed, the admin redirect, the Google button and its
first redirect to Google, onboarding through to setting a password, the admin's add screen and
actions, Content Editor permissions, `ADMIN_URL_PATH`), `test_user_model.py`. The full Google round
trip is a manual check on each host (`Phase_1/Test_Plan.md` §4).
