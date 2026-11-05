# Phase 1 · Day 7: Nunito Sans, the Services page, and enquiries saved and emailed

**Cards:** `Phase_1/Task_Breakdown.md`, Day 7
**Completed:** 2026-11-04 · **Revised:** —

Run from the repo root. Commands are bash; on Windows or macOS see
[`../Terminal_Note.md`](../Terminal_Note.md).

## 1. Put the files in place

```bash
git checkout main && git pull
git checkout -b day-7
unzip -o ../distinctive-site-day7.zip -d ..
# Unzipping can't delete: the Open Sans files are replaced by Nunito Sans.
git rm -rq static/vendor/open-sans
git status --short | head -60
```

```powershell
git checkout main; git pull
git checkout -b day-7
Expand-Archive -Force ..\distinctive-site-day7.zip ..
git rm -rq static/vendor/open-sans
git status --short
```

**Expect:** changed `package.json` and `package-lock.json` (`@fontsource/nunito-sans` instead of
`@fontsource/open-sans`), `scripts/copy-vendor.mjs`, `static/scss/_fonts.scss`, `_tokens.scss`,
`admin.scss`, both compiled CSS files and `templates/base.html`; new `static/vendor/nunito-sans/`;
the Open Sans files as `D`; new files in `apps/contact/` (model, admin, repository, service,
migration, tests); migrations `pages/0004_service_bands.py` and
`offerings/0002_image_on_services_page.py`; `templates/includes/_service_bands.html`;
`static/scss/components/_services.scss`; 11 new images in `apps/core/seed/images/`; changed docs.

## 2. Node packages and the CSS

```bash
npm ci
npm run vendor
npm run build:css
git status --short static/ templates/includes/icons/
```

**Expect:** `npm run vendor` lists the six `nunito-sans-latin-…woff2` files; then nothing new from
`git status` (the committed fonts, icons and CSS are what the packages produce).

## 3. Start and migrate

No Python package changed; `--build` is harmless.

```bash
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml logs --tail 20 web
```

**Expect:** `Applying contact.0001_initial… OK`, `Applying offerings.0002_image_on_services_page…
OK`, `Applying pages.0004_service_bands… OK`, then the development server starting.

## 4. Load the Services content

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
```

**Expect:** on a database seeded on Days 5–6, the first run prints
`Added 7 services, 10 clients, 3 sections. Filled in empty fields on 6 existing item(s).` (Home's
six services get their full text; their summaries, order and "show on Home" are untouched). The
second prints `Nothing to add: the content is already there.`

## 5. The font

Open <http://localhost:8000/> and <http://localhost:8000/admin/>.

**Expect:** both in Nunito Sans (rounder than before; in DevTools → Elements → Computed →
`font-family`, the rendered font is "Nunito Sans"). The Network tab shows
`nunito-sans-latin-400-normal.woff2` loaded from `/static/`, nothing from Google.

## 6. The Services page

Open <http://localhost:8000/services/> at full width, then at phone width (375 px).

**Expect:**

- **Our Services** in gold on black, with the "What We Do" paragraph below it.
- **What We Do** with a link for each of the 13 services. Click **Team Building**: the page
  scrolls to its band, just below the sticky navbar.
- Thirteen bands alternating black (heading on the right; on the left on a phone) and white.
  Long lists (Learning and Development's training products) are in two columns on a wide screen.
- **NGO Capacity Development Partners** with the five areas as text and the diagram beside them.
- **Some of Our Corporate Clients**: ten logos, five to a row.

Open <http://localhost:8000/> and click a service card.

**Expect:** the Services page opens at that service's band.

## 7. An enquiry saved and "emailed" (console)

With the default `EMAIL_PROVIDER=console`:

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py shell -c "
from apps.contact.services.contact_service import ContactService
s = ContactService().submit({'name': 'Test Visitor', 'email': 'visitor@example.org', 'message': 'Testing Day 7.'}, source_page='services')
print('saved', s.pk, 'email_sent', s.email_sent)"
```

**Expect:** the email printed (the console backend writes it where the command runs):
`Subject: Website enquiry from
Test Visitor (Services page)`, `To: enquiries@distinctive.co.zw` (or your `CONTACT_RECIPIENT`),
`Reply-To: visitor@example.org`, and the message as plain text; then `saved 1 email_sent True`.

## 8. Enquiries in the admin

Open <http://localhost:8000/admin/contact/contactsubmission/>.

**Expect:** **Enquiries** first in the menu; the test enquiry with **Email sent** ✔ and
**Handled** ✘; no "Add" button. Tick it, choose **Mark as handled**, **Go**: "Marked 1
enquiry(ies) as handled." Choose **Resend notification email**: "Sent 1 notification email(s)."

## 9. A real send through Resend (owner, once the domain is verified)

Needs the Resend setup in `deployment.md` §6 (the sending domain **Verified**, a Sending-access
key). In `.env`, temporarily:

```bash
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_…
DEFAULT_FROM_EMAIL=Distinctive Website <website@mail.distinctive.co.zw>
CONTACT_RECIPIENT=you@your-mailbox
```

```bash
docker compose -f docker/docker-compose.yml up -d
docker compose -f docker/docker-compose.yml exec web python manage.py sendtestemail you@your-mailbox
```

**Expect:** no `core.W00x` warnings in the start-up log, and the test email in your inbox. Then
repeat step 7.

**Expect:** `email_sent True` (nothing printed: Resend sent it) and the enquiry in your inbox; **Reply** addresses
`visitor@example.org`. With a wrong key instead, step 7 prints `email_sent False`, the admin shows
the provider's message on the enquiry, and **Resend notification email** works once the key is
fixed. Put `.env` back to `EMAIL_PROVIDER=console` afterwards.

## 10. The CI checks

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
```

**Expect:** `All checks passed!`; `… files already formatted`; `0 errors, 0 warnings, 0 notes`;
`No changes detected`; `209 passed` with `Required test coverage of 85% reached`.

## 11. The image's static step and the deploy check

```bash
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e EMAIL_PROVIDER=console web python manage.py collectstatic --noinput --dry-run | tail -1
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e ALLOWED_HOSTS=example.org -e EMAIL_PROVIDER=console web python manage.py check --deploy
```

**Expect:** a file count with no `MissingFileError` (the fonts are referenced from the new
folder), and `System check identified no issues (2 silenced).`

## 12. Commit, push and open a PR

```bash
git add -A
git commit -m "Phase 1 Day 7: Nunito Sans, Services page, enquiries saved and emailed"
git push -u origin day-7
```

**Expect:** `test` and `css-fresh` both pass on the PR. Merge it.
