# Phase 1 · Day 10: SEO, redirects, responsive images, production files and the demo

**Cards:** `Phase_1/Task_Breakdown.md`, Day 10
**Completed:** 2026-11-05 (the code; steps 8, 10 and 11 are the owner's) · **Revised:** 2026-11-09 (the admin with production static storage: 306 tests)

Run from the repo root. Commands are bash; on Windows or macOS see
[`../Terminal_Note.md`](../Terminal_Note.md). Steps 1–9 are on your machine; step 10 merges, which
builds the image; step 11 puts the demo on the VPS.

## 1. Put the files in place

Day 9 must be merged first (its zip already carried most of today's SEO and redirect code).

```bash
git checkout main && git pull
git checkout -b day-10
unzip -o ../distinctive-site-day10.zip -d ..
git status --short | head -40
```

```powershell
git checkout main; git pull
git checkout -b day-10
Expand-Archive -Force ..\distinctive-site-day10.zip ..
git status --short
```

**Expect:** new `apps/core/services/image_variant_service.py`,
`apps/core/tests/test_image_variant_service.py`, `docs/commands/Phase_1/day-10.md` and the
error-log entry `docs/errors-and-exceptions/row-g5-gutter-made-phones-scroll-sideways__…/`;
changed `templates/includes/_image.html` and the templates that include it (each now passes a
`sizes`), `_section.html`, `_service_bands.html` and `_footer.html` (`g-4 g-lg-5`),
`_hero.scss` and both compiled CSS files, `core_extras.py`, `test_polish.py`,
`docker/docker-compose.prod.yml` and `.env.prod.example` (comments), and the docs.

## 2. The CSS

```bash
npm ci
npm run build:css
git status --short static/css/
```

**Expect:** no output from `git status`.

## 3. Start

No new packages or migrations today.

```bash
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml exec web python manage.py migrate
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
```

**Expect:** `No migrations to apply.` and `Nothing to add: the content is already there.`

## 4. Search and sharing tags, robots and the sitemap

Open <http://localhost:8000/>, then View Page Source (Ctrl+U).

**Expect,** in `<head>`:
- `<title>Distinctive Consultancy Services | HR Consultancy, Harare</title>` (Home's search
  title, from the admin's **Search engines** tab), a meta description, and
  `<link rel="canonical" href="http://localhost:8000/">`.
- `og:` and `twitter:` tags with the same title, description and an image address.
- A `<script type="application/ld+json">` block: the `Organization`, with the address and
  phone. About, Services and Contact have their own titles and canonicals, and no JSON-LD.

```bash
curl -s http://localhost:8000/robots.txt
curl -s http://localhost:8000/sitemap.xml
```

**Expect:** `robots.txt` reads `User-agent: *`, `Disallow: /accounts/`, then
`Sitemap: http://localhost:8000/sitemap.xml`; the admin's address isn't in it. The sitemap lists
the four pages, each with a `<lastmod>`.

## 5. Old addresses

```bash
curl -sI http://localhost:8000/about-us/ | grep -i -E "^HTTP|^location"
curl -sI http://localhost:8000/jobs/hr-officer/ | grep -i -E "^HTTP|^location"
curl -sI http://localhost:8000/about/ | grep -i "^HTTP"
```

**Expect:** `301 Moved Permanently` with `Location: /about/`; `302 Found` with
`Location: /contact/` (jobs go to Contact until Phase 2, temporarily so it can change then);
`200 OK` (a live page is never redirected).

Open the admin → **Redirects**.

**Expect:** nine redirects; `/about-us/` and `/jobs/` now show **hits** of 1 and a **last used**
time.

## 6. The 404 page

Open <http://localhost:8000/no-such-page/>.

**Expect:** "We couldn't find that page" on the black band with the site's header and footer,
buttons for the four pages, and the enquiries email and phone. DevTools → Network shows status
**404**. (The 500 page is checked by the tests: it needs no database or context, so it still
shows when those are what broke.)

## 7. Responsive images

Open <http://localhost:8000/> with DevTools → Network → filter **Img**, and the device toolbar
set to a phone (Ctrl+Shift+M, iPhone 12 Pro).

**Expect:** the hero loads `team-photo.webp` from `/media/variants/800/pages/slides/` (about
90 KB), not `team-photo.jpg` (280 KB). At full width on a large screen it loads the 1600 px JPEG
or a larger copy. The copies are files:

```bash
docker compose -f docker/docker-compose.yml exec web find media/variants -name "*.webp" | head
```

**Expect:** a few `.webp` files under `media/variants/<width>/…`, made on the first visit.

## 8. The old site's sitemap (owner)

Save the live site's sitemap and the sitemaps it lists (open them in a browser and Save As, into
the repo root; they aren't committed):

- <https://distinctive.co.zw/wp-sitemap.xml> (WordPress's own), or
  <https://distinctive.co.zw/sitemap_index.xml> (if an SEO plugin made one)

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py check_redirects wp-sitemap.xml
```

**Expect:** for an index, the list of child sitemaps to save too; for each sitemap, one line per
address, `OK → …` or `MISSING`, and a summary. Run it again with the child sitemaps. For every
`MISSING`, add a redirect in the admin (**Redirects → Add**), then re-run until nothing is
missing. Don't commit the sitemap files.

## 9. The CI checks

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e ALLOWED_HOSTS=example.org -e EMAIL_PROVIDER=console web python manage.py check --deploy
```

**Expect:** `All checks passed!`; `… files already formatted`; `0 errors, 0 warnings, 0 notes`;
`No changes detected`; `306 passed` with `Required test coverage of 85% reached`;
`System check identified no issues (2 silenced).`

## 10. Merge, which builds the image

```bash
git add -A
git commit -m "Phase 1 Day 10: SEO, redirects, responsive images, production files"
git push -u origin day-10
```

**Expect:** `test` and `css-fresh` pass on the PR. Merge it. On `main`, the **CI** run's third job,
`build-and-push`, pushes `ghcr.io/<owner>/<repo>:latest` and `:<commit SHA>`; the image appears
under the repository's **Packages**.

**Optional, before the VPS:** the whole prod stack on your machine.

```bash
docker build -f docker/Dockerfile -t ghcr.io/<owner>/<repo>:local .
cp .env.prod.example .env.prod
# In .env.prod: SECRET_KEY, POSTGRES_PASSWORD, GHCR_IMAGE=<owner>/<repo>, IMAGE_TAG=local,
# SITE_DOMAIN=localhost, SITE_URL=https://localhost, ALLOWED_HOSTS=localhost,
# CSRF_TRUSTED_ORIGINS=https://localhost, EMAIL_PROVIDER=console, ENV_FILE=../.env.prod
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml up -d
docker compose --env-file .env.prod -f docker/docker-compose.prod.yml logs --tail 30 web
```

**Expect:** the migrations, `Added …` from the seed, then gunicorn's `Booting worker` lines.
<https://localhost> (accept Caddy's local certificate) shows the site; an image uploaded in the
admin shows on the page, served by Caddy. Stop it with `… down` (not `down -v`, which deletes
its data). If the demo can't go on the VPS today, this is also how to show it on your laptop.

## 11. The demo on the preview host (owner)

`deployment.md` §7 and §8 have the reasons; this is the order.

**On the server (once):** Ubuntu 24.04, a `deploy` user in the `docker` group, SSH keys only,
`ufw allow 22,80,443/tcp`, Docker Engine with the Compose plugin. Then, as `deploy`:

```bash
sudo mkdir -p /srv/distinctive && sudo chown deploy: /srv/distinctive && cd /srv/distinctive
# Copy docker/docker-compose.prod.yml, docker/Caddyfile and .env.prod.example here (scp), then:
mv .env.prod.example .env && chmod 600 .env
echo "<token with read:packages>" | docker login ghcr.io -u <github-username> --password-stdin
```

**Expect:** `Login Succeeded`.

**`.env`:** a new `SECRET_KEY` and `POSTGRES_PASSWORD`; `GHCR_IMAGE=<owner>/<repo>` in lower case;
`SITE_DOMAIN=new.distinctive.co.zw` with `SITE_URL`, `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
to match; `SEO_NOINDEX=true`; `SEED_SITE_CONTENT=true`; a real `ADMIN_URL_PATH`;
`EMAIL_PROVIDER=console` until Resend is verified (enquiries are still saved in the admin), then
`resend` with its key.

**DNS:** an `A` record `new` → the server's IP (DNS only, not proxied). Check it before deploying:

```bash
dig +short new.distinctive.co.zw
```

**Expect:** the server's IP.

**GitHub:** Settings → Environments → `production`: secrets `VPS_HOST`, `VPS_USER` (`deploy`),
`VPS_SSH_KEY` (a key just for this), `VPS_APP_DIR` (`/srv/distinctive`), `VPS_KNOWN_HOSTS` (from
`ssh-keyscan -t ed25519 <server>`), and the variable `SITE_URL=https://new.distinctive.co.zw`.
Then Actions → **Deploy VPS** → **Run workflow** (`latest`).

**Expect:** the run ends with `healthy`. <https://new.distinctive.co.zw> shows the site with a
valid certificate; View Source shows `<meta name="robots" content="noindex, nofollow">`, and
`/robots.txt` reads `Disallow: /`. On the server:

```bash
cd /srv/distinctive
docker compose -f docker-compose.prod.yml logs --tail 40 web
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

**Expect:** in the log, the migrations and `Added …` from the seed, and no `core.W00x` warnings
(with `EMAIL_PROVIDER=resend`, a `W001` or `W002` means the sender or key is missing). Then remove `SEED_SITE_CONTENT` from
`.env` (so later deploys don't run it), sign in at `/<ADMIN_URL_PATH>` (the admin's index must
open; until 2026-11-09 it answered 500 under production settings, see the error log), send a test
enquiry from the Contact page and see it in the admin. The site is ready to walk the stakeholders through.
