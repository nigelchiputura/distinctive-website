# Phase 1 · Day 5: Pages, Home and the services, with the first part of the seed

**Cards:** `Phase_1/Task_Breakdown.md`, Day 5
**Completed:** 2026-11-03 · **Revised:** —

Run from the repo root. Commands are bash; on Windows or macOS see
[`../Terminal_Note.md`](../Terminal_Note.md).

## 1. Put the files in place

```bash
git checkout main && git pull
git checkout -b day-5
unzip -o ../distinctive-site-day5.zip -d ..
# Unzipping can't delete: remove Day 1's placeholder home page, which Home replaces.
git rm -q apps/core/controllers/placeholder_controller.py apps/core/templates/core/placeholder.html
git status --short | head -50
```

```powershell
git checkout main; git pull
git checkout -b day-5
Expand-Archive -Force ..\distinctive-site-day5.zip ..
git rm -q apps/core/controllers/placeholder_controller.py apps/core/templates/core/placeholder.html
git status --short
```

**Expect:** new `apps/pages/` and `apps/offerings/` files (models, admin, repositories, services,
the home controller, migrations, tests), `apps/core/seed/` (content and 8 images),
`apps/core/services/seed_service.py`, `apps/core/management/commands/seed_site_content.py`, new
templates in `templates/includes/`, `static/js/`, three new SCSS partials, a changed
`static/css/main.css`, a new folder in `docs/errors-and-exceptions/`, changed docs; and the two placeholder files listed as `D` (deleted).

## 2. Start and migrate

No package changed, so no rebuild is needed; `--build` is harmless.

```bash
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml logs --tail 20 web
```

**Expect:** `Applying offerings.0001_initial… OK`, `Applying pages.0001_initial… OK`,
`Applying pages.0002_the_four_pages… OK`, then the development server starting.

## 3. The CSS is up to date

```bash
npm ci
npm run build:css
git status --short static/css/
```

**Expect:** no warnings, and nothing from `git status`.

## 4. Home before the seed

Open <http://localhost:8000/>.

**Expect:** the top bar, navbar and footer with an empty page between them. Home works on a fresh
database (the four pages exist from the migration); it just has no content yet.

## 5. Load Home's content

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
```

**Expect:** the first run prints `Added 6 services, 1 hero slide, 4 sections.`; the second
`Nothing to add: the content is already there.`

## 6. Home after the seed

Reload <http://localhost:8000/> at full width, then narrow the window to tablet and phone width
(or use the browser's device toolbar at 768 and 375 px).

**Expect:** "Distinctive Consultancy Services" in gold on a black hero with "BRINGING EXCELLENCE
INTO YOUR WORLD." below; a charcoal band with six framed service cards (three across on a wide
screen, one on a phone); "Get the best specialised business consultancy services in Africa."
with a gold **Get In Touch** button; then **People Centred** (image left) and **Proactive**
(image right; on a phone every image comes first). Hovering a card underlines its title; its
link goes to `/services/#…` (Services itself arrives on Day 7, so that page is still a 404).

## 7. Edit Home in the admin

Sign in at <http://localhost:8000/admin/> and open **Pages → Home**.

**Expect:** tabs **General**, **Search engines**, **Hero slides**, **Sections**.

On **Sections**, change **Proactive**'s order from 40 to 25 and save. Reload Home.

**Expect:** Proactive now comes before People Centred. Set it back to 40.

On **Hero slides**, add a second slide (a heading is enough) and save. Reload Home.

**Expect:** arrows, dots and a **Pause slides** button; the slides change every 6 seconds, stop
while the pointer is over them, and stay put after **Pause slides** until **Play slides**. With
your system's "reduce motion" setting on, they don't move by themselves and the pause button
isn't shown. Delete the test slide (tick **Delete** on it, save).

Try saving a section with an image but no **Image description**.

**Expect:** "Describe the image, or tick “decorative image” if it needs no description."

## 8. The services list

Open **Services → Services**.

**Expect:** six services with thumbnails; "Show on Home", "Order" and "Published" editable in
the list. Untick "Show on Home" on one, save, reload Home: five cards. Tick it again.

## 9. The CI checks

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
```

**Expect:** `All checks passed!`; `… files already formatted`; `0 errors, 0 warnings, 0 notes`;
`No changes detected`; `167 passed` with `Required test coverage of 85% reached`.

## 10. The image's static step and the deploy check

```bash
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e EMAIL_PROVIDER=console web python manage.py collectstatic --noinput --dry-run | tail -1
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e ALLOWED_HOSTS=example.org -e EMAIL_PROVIDER=console web python manage.py check --deploy
```

**Expect:** a file count with no `MissingFileError`, and
`System check identified no issues (2 silenced).`

## 11. Commit, push and open a PR

```bash
git add -A
git commit -m "Phase 1 Day 5: pages, Home, services, seed part 1"
git push -u origin day-5
```

**Expect:** `test` and `css-fresh` both pass on the PR. Merge it.
