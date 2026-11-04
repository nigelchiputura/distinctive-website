# Phase 1 · Day 3: Base classes, site settings, Markdown, layering and email checks

**Cards:** `Phase_1/Task_Breakdown.md`, Day 3
**Completed:** 2026-11-03 · **Revised:** —

Run from the repo root. Commands are bash; on Windows or macOS see
[`../Terminal_Note.md`](../Terminal_Note.md).

## 1. Put the files in place

```bash
git checkout main && git pull
git checkout -b day-3
unzip -o ../distinctive-site-day3.zip -d ..
git status --short | head -40
```

```powershell
git checkout main; git pull
git checkout -b day-3
Expand-Archive -Force ..\distinctive-site-day3.zip ..
git status --short
```

**Expect:** changed `requirements/base.txt` (four new packages), new migrations in
`apps/core/migrations/` and `apps/users/migrations/`, new files in `apps/core/` and
`apps/users/managers.py`, `config/settings/email.py`, a new `static/img/logo.png`, and changed
docs.

## 2. Rebuild (requirements changed)

```bash
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml logs --tail 20 web
```

**Expect:** the image installs `django-anymail`, `Markdown`, `nh3` and `pillow`; then
`Applying core.0001_site_settings… OK`, `Applying core.0002_site_settings_row… OK`,
`Applying users.0002_email_login_manager… OK`, then the development server starting.

Without `--build` the container stops with `requirements/ has changed since this image was
built`. That's the guard working: run the command above.

## 3. The CSS hasn't changed

```bash
npm run build:css
git status --short static/css/
```

**Expect:** no output from `git status` (no SCSS changed today).

## 4. The new logo and the site's details from the database

Open <http://localhost:8000>.

**Expect:** the client's logo in the navbar (sharp-edged, on a transparent background), and the
same phone, email, address and hours as before. They now come from the **Site settings** row,
which the migration filled with the old site's details.

## 5. Edit the site settings in the admin

Sign in at <http://localhost:8000/admin/> and click **Site settings**.

**Expect:** it opens straight on the single settings form (there's no list and no "Add" button).

Type `facebook.com/your-page` into **Facebook** (without `https://`) and **Save**.

**Expect:** the field now reads `https://facebook.com/your-page`; on the home page a Facebook
icon appears at the right of the top bar and in the footer. Clear the field and save again to
hide it.

## 6. `createsuperuser` asks only for an email (optional)

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py createsuperuser
```

**Expect:** prompts for **Email address** and **Password** only (no username). Press Ctrl+C to
stop if you don't need another account.

## 7. The email checks

With the production settings, no sender and no key:

```bash
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e ALLOWED_HOSTS=example.org -e DEFAULT_FROM_EMAIL= -e RESEND_API_KEY= web python manage.py check
```

**Expect:** two warnings: `core.W001` (`DEFAULT_FROM_EMAIL … isn't on a real domain`) and
`core.W002` (`EMAIL_PROVIDER is 'resend' but RESEND_API_KEY is empty`). On the VPS these appear in
the logs at every start until the settings are right.

With a mistyped provider:

```bash
docker compose -f docker/docker-compose.yml exec -e EMAIL_PROVIDER=gmail web python manage.py check
```

**Expect:** `ImproperlyConfigured: EMAIL_PROVIDER='gmail' isn't one of: console, resend, smtp.`

## 8. The checks CI runs

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
```

**Expect:** `All checks passed!`; `… files already formatted`; `0 errors, 0 warnings, 0 notes`;
`No changes detected`; `101 passed` with `Required test coverage of 85% reached`.

## 9. Deploy check

```bash
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e ALLOWED_HOSTS=example.org -e EMAIL_PROVIDER=console web python manage.py check --deploy
```

**Expect:** `System check identified no issues (2 silenced).`

## 10. Commit, push and open a PR

```bash
git add -A
git commit -m "Phase 1 Day 3: base classes, site settings, Markdown, layering and email checks"
git push -u origin day-3
```

**Expect:** `test` and `css-fresh` both pass on the PR. Merge it.
