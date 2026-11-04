# Phase 1 · Day 8: the Contact page, the Services enquiry block and cookie consent

**Cards:** `Phase_1/Task_Breakdown.md`, Day 8
**Completed:** 2026-11-04 · **Revised:** —

Run from the repo root. Commands are bash; on Windows or macOS see
[`../Terminal_Note.md`](../Terminal_Note.md).

## 1. Put the files in place

```bash
git checkout main && git pull
git checkout -b day-8
unzip -o ../distinctive-site-day8.zip -d ..
git status --short | head -60
```

```powershell
git checkout main; git pull
git checkout -b day-8
Expand-Archive -Force ..\distinctive-site-day8.zip ..
git status --short
```

**Expect:** new `apps/contact/forms.py`, `apps/contact/controllers/contact_controller.py`,
`apps/contact/urls.py`, `apps/core/services/rate_limit_service.py`, `apps/conftest.py`, the
migration `pages/0005_form_and_map_sections.py`, `templates/includes/_enquiry_form.html` and
`_cookie_banner.html`, `static/js/modules/http.js`, `contact-form.js` and `cookie-consent.js`,
`static/scss/components/_forms.scss`, `_contact.scss` and `_cookie-banner.scss`, and new tests;
changed settings, `config/urls.py`, `docker/entrypoint.sh`, `.env.example`, the page
controller, templates, `main.js`, the SCSS, both compiled CSS files, the seed and docs. Nothing
deleted.

## 2. The CSS

```bash
npm ci
npm run build:css
git status --short static/css/
```

**Expect:** no output from `git status`: the committed CSS is what the SCSS produces.

## 3. Start, migrate and the cache table

No Python package changed. The entrypoint now also runs `createcachetable`.

```bash
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml logs --tail 20 web
```

**Expect:** `Applying pages.0005_form_and_map_sections… OK`, then the development server
starting. The cache table is created silently (it prints nothing, now or on later starts).

## 4. Load the Contact content

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
```

**Expect:** on a database seeded on Days 5–7, the first run prints `Added 3 sections.` (Contact's
form and map, and the Services enquiry block); the second prints
`Nothing to add: the content is already there.`

## 5. The Contact form with JavaScript on

Open <http://localhost:8000/contact/>. (No banner yet: with no GA4 id and no Maps key there is
nothing to ask about. Step 8 turns it on.)

**Expect:** a black band with **Get In Touch!**, Name and Email Address side by side, Message,
an outlined gold **Submit**; on the right a gold-framed **Reach Us** box with the address, phone,
email, hours and "Vacancies: Send your CV to recruitment@distinctive.co.zw". Below, **Find Us**
with the address and **Get directions** (opens Google Maps in a new tab).

Press **Submit** with the form empty.

**Expect:** without a reload, a sentence under each field ("Please enter your name." …), the
fields outlined, and the cursor in Name. Fill in all three and press **Submit**.

**Expect:** the form is replaced by "Thank you, your message has been sent. We'll get back to you
soon." The email is printed in the web container's log:

```bash
docker compose -f docker/docker-compose.yml logs --tail 40 web
```

**Expect:** `Subject: Website enquiry from <your name> (Contact page)` and `Reply-To:` your
address. In <http://localhost:8000/admin/contact/contactsubmission/> the enquiry shows **Sent
from: Contact page**, **Email sent** ✔.

## 6. The same with JavaScript off, and the Services block

In Chrome: DevTools → ⋮ → Run command → "Disable JavaScript". Reload `/contact/`, fill in the
form, press **Submit**.

**Expect:** a full page load back to `/contact/#contact-form` with the thank-you above the form,
and a second enquiry in the admin. Submit it empty instead: the page comes back with the errors
under the fields and what you typed kept. Turn JavaScript back on.

Open <http://localhost:8000/services/#get-in-touch>.

**Expect:** after the client logos, a gold band **Get In Touch With Us** with First Name and Last
Name side by side, Email Address, Message and a black **Send enquiry**. Send one: the same
thank-you, and the admin shows it with **Sent from: Services page** and the two names joined.

## 7. The rate limit

Send three more enquiries from `/contact/` (five in all from your machine in the last hour), then
one more.

**Expect:** the sixth shows "You've sent us several messages in the last hour. Please try again
later, or email us at enquiries@distinctive.co.zw." and nothing new in the admin. To start again:

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

## 8. Cookie consent (with placeholder values)

In `.env`, temporarily:

```bash
GA_MEASUREMENT_ID=G-TEST123
GOOGLE_MAPS_EMBED_KEY=placeholder
```

```bash
docker compose -f docker/docker-compose.yml up -d
```

Open a **private window**, DevTools → Network, filter `google`, and open
<http://localhost:8000/contact/>.

**Expect:**

- A black bar at the bottom, **Cookies on this site**, with **Accept** and **Decline**; under
  the map's address, "The map uses cookies from Google, so it shows once you accept cookies."
- **No request** in the Network tab.

Press **Decline**, then reload.

**Expect:** no banner and still no request. Press **Cookie settings** in the footer: the bar
comes back with Accept focused. Press **Accept**.

**Expect:** requests to `googletagmanager.com/gtag/js` and `google.com/maps/embed/v1/place`. The
map frame shows Google's "key invalid" message (the placeholder key): that is expected here. Open
`/about/`: no banner, and `gtag/js` loads straight away. Reopen **Cookie settings** and
**Decline**: on the next page nothing goes to Google, and the `_ga` cookies are gone (DevTools →
Application → Cookies).

Put `.env` back (empty values) and `up -d` again.

## 9. The real Maps key and GA4 (owner, before Day 10)

1. Google Cloud Console → the project → APIs & Services → enable **Maps Embed API** → Credentials →
   **Create credentials → API key**. Restrict it: **Websites** →
   `https://new.distinctive.co.zw/*`, `https://distinctive.co.zw/*`,
   `https://www.distinctive.co.zw/*` (and `http://localhost:8000/*` for testing locally);
   **API restrictions** → Maps Embed API only.
2. GA4 → Admin → Create property "Distinctive website" → Web stream for `distinctive.co.zw` →
   copy the **Measurement ID** (`G-…`).
3. Put the key in the VPS `.env` as `GOOGLE_MAPS_EMBED_KEY`, and the ID in the admin's **Site
   settings** (or `GA_MEASUREMENT_ID` in `.env`).

**Expect:** on the preview host, after **Accept**, the map of 62 Mutare Road shows (the old site's
"can't load Google Maps correctly" error does not), and GA4 → Reports → Realtime shows your
visit.

## 10. The CI checks

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
```

**Expect:** `All checks passed!`; `… files already formatted`; `0 errors, 0 warnings, 0 notes`;
`No changes detected`; `249 passed` with `Required test coverage of 85% reached`.

## 11. The image's static step and the deploy check

```bash
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e EMAIL_PROVIDER=console web python manage.py collectstatic --noinput --dry-run | tail -1
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e ALLOWED_HOSTS=example.org -e EMAIL_PROVIDER=console web python manage.py check --deploy
```

**Expect:** a file count with no `MissingFileError`, and
`System check identified no issues (2 silenced).`

## 12. Commit, push and open a PR

```bash
git add -A
git commit -m "Phase 1 Day 8: Contact page, Services enquiry block, cookie consent"
git push -u origin day-8
```

**Expect:** `test` and `css-fresh` both pass on the PR. Merge it.
