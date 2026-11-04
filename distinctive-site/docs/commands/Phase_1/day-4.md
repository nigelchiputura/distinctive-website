# Phase 1 · Day 4: Sign-in (allauth), onboarding, the Content Editor group, the admin theme

**Cards:** `Phase_1/Task_Breakdown.md`, Day 4
**Completed:** 2026-11-03 · **Revised:** —

Run from the repo root. Commands are bash; on Windows or macOS see
[`../Terminal_Note.md`](../Terminal_Note.md).

## 1. Put the files in place

```bash
git checkout main && git pull
git checkout -b day-4
unzip -o ../distinctive-site-day4.zip -d ..
git status --short | head -40
```

```powershell
git checkout main; git pull
git checkout -b day-4
Expand-Archive -Force ..\distinctive-site-day4.zip ..
git status --short
```

**Expect:** changed `requirements/base.txt` (allauth and Jazzmin), `config/settings/base.py`,
`config/urls.py`, `package.json`; new files in `apps/users/`, `templates/allauth/`,
`templates/account/`, `static/scss/admin.scss`, `static/scss/components/_auth.scss`,
`static/css/admin.css`; a new folder in `docs/errors-and-exceptions/`; changed docs.

## 2. Rebuild (requirements changed)

```bash
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml logs --tail 30 web
```

**Expect:** the image installs `django-allauth` and `django-jazzmin`; the migrations for
`sites`, `account` and `socialaccount`, then `Applying users.0003_site_name… OK`; then the
development server starting.

## 3. The CSS is up to date

```bash
npm ci
npm run build:css
git status --short static/css/
```

**Expect:** no warnings, and nothing from `git status` (both `main.css` and the new `admin.css`
are committed as compiled).

## 4. The sign-in page

Open <http://localhost:8000/admin/>.

**Expect:** you're sent to **Staff sign in** at `/accounts/login/?next=/admin/`, in the site's
own layout (top bar with the phone and email, footer below). No "sign up" link and, until Google
is configured (step 9), no Google button. Sign in with your superuser.

**Expect:** the Jazzmin admin: the logo on a white strip at the top of a dark sidebar, "View
website" in the top bar, and **Site settings**, **Users** and **Groups** in the menu.

## 5. Sign-up is closed

Open <http://localhost:8000/accounts/signup/>.

**Expect:** "Sign Up Closed".

## 6. Add a user from the admin

**Users → Add user**: an email you can read (for example your own with `+editor` before the
`@`), a first and last name. **Content Editor** is already ticked. Save.

**Expect:** "A set-password link was emailed to …". Locally the email prints in the log:

```bash
docker compose -f docker/docker-compose.yml logs web | grep -A12 "Your Distinctive website account"
```

**Expect:** the email, with a link like
`http://localhost:8000/accounts/password/reset/key/2-…/`.

## 7. Set the password and sign in as the editor

Open the link in a **private window** (so you stay signed in as the superuser in the other).

**Expect:** **Set your password**. Enter a password of 12 or more characters twice, then
**Set password**, then **Sign in** with the new user's email and password.

**Expect:** the admin shows only **Site settings**. Opening
<http://localhost:8000/admin/users/user/> gives **403 Forbidden**.

Open the link again.

**Expect:** "This link has expired" (links work once).

## 8. Onboard from the command line (optional)

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py onboard_user someone@example.org --first Someone --no-email
```

**Expect:** `Created someone@example.org (group: Content Editor).` and the set-password link
printed. Running it again fails with `… already has an account.`

## 9. Google sign-in (ONE-TIME setup, then a check)

In the Google Cloud console (<https://console.cloud.google.com>), in a project for the website:

1. **APIs & Services → OAuth consent screen**: app name "Distinctive website", a support email,
   scopes `email` and `profile`. While testing, add your own Google account as a test user.
2. **APIs & Services → Credentials → Create credentials → OAuth client ID**, type **Web
   application**, with these **Authorised redirect URIs**:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `https://new.distinctive.co.zw/accounts/google/login/callback/`
   - `https://distinctive.co.zw/accounts/google/login/callback/`
3. Copy the client ID and secret into `.env`:

```bash
GOOGLE_CLIENT_ID=…apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=…
```

Then restart and check:

```bash
docker compose -f docker/docker-compose.yml up --build -d
```

**Expect:** **Sign in with Google** under the sign-in form. With a Google account whose address
matches a staff user (add one in step 6 if needed), it signs you in and lands in the admin. With
any other Google account it returns to the sign-in page saying "That Google account isn't linked
to a staff account on this website…".

## 10. The checks CI runs

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
```

**Expect:** `All checks passed!`; `… files already formatted`; `0 errors, 0 warnings, 0 notes`;
`No changes detected`; `134 passed` with `Required test coverage of 85% reached`.

## 11. The image's static step and the deploy check

```bash
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e EMAIL_PROVIDER=console web python manage.py collectstatic --noinput --dry-run | tail -1
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e ALLOWED_HOSTS=example.org -e EMAIL_PROVIDER=console web python manage.py check --deploy
```

**Expect:** a file count with no `MissingFileError` (a notice about a duplicate
`admin/js/cancel.js` is normal: Jazzmin replaces Django's), and
`System check identified no issues (2 silenced).`

## 12. Commit, push and open a PR

```bash
git add -A
git commit -m "Phase 1 Day 4: sign-in, onboarding, Content Editor group, admin theme"
git push -u origin day-4
```

**Expect:** `test` and `css-fresh` both pass on the PR. Merge it.
