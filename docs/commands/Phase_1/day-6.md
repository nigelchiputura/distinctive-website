# Phase 1 · Day 6: About, the team and the partners, with the second part of the seed

**Cards:** `Phase_1/Task_Breakdown.md`, Day 6
**Completed:** 2026-11-04 · **Revised:** —

Run from the repo root. Commands are bash; on Windows or macOS see
[`../Terminal_Note.md`](../Terminal_Note.md).

## 1. Put the files in place

```bash
git checkout main && git pull
git checkout -b day-6
unzip -o ../distinctive-site-day6.zip -d ..
# Unzipping can't delete: Home's controller moved into page_controller.py.
git rm -q apps/pages/controllers/home_controller.py
git status --short | head -50
```

```powershell
git checkout main; git pull
git checkout -b day-6
Expand-Archive -Force ..\distinctive-site-day6.zip ..
git rm -q apps/pages/controllers/home_controller.py
git status --short
```

**Expect:** new files in `apps/team/` (model, admin, repository, service, migration, tests) and
`apps/pages/` (`page_controller.py`, `partner_repository.py`, `partner_service.py`,
`page_blocks_service.py`, migration `0003_partner_section_layout.py`, `templates/pages/page.html`,
tests); 11 new images in `apps/core/seed/images/`; `templates/includes/_logo_grid.html` and
`_team_card.html`; `static/js/modules/read-more.js`; two new SCSS partials and a changed
`static/css/main.css`; changed docs; and `home_controller.py` listed as `D` (deleted).

## 2. Start and migrate

No package changed; `--build` is harmless.

```bash
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml logs --tail 20 web
```

**Expect:** `Applying pages.0003_partner_section_layout… OK` and `Applying team.0001_initial… OK`,
then the development server starting.

## 3. The CSS is up to date

```bash
npm ci
npm run build:css
git status --short static/css/
```

**Expect:** no warnings, and nothing from `git status`.

## 4. Load About's content

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
```

**Expect:** on a database seeded on Day 5, the first run prints
`Added 8 team members, 2 partners, 6 sections.` (on an empty one, Home's items too); the second
`Nothing to add: the content is already there.` Home is unchanged.

## 5. About

Open <http://localhost:8000/about/> at full width, then at tablet (768 px) and phone (375 px)
width.

**Expect:**

- **Bringing Excellence Into Your World!** in gold on black, with "About Us" marked in the navbar.
- **Our Story** on a dark-navy-to-blue band: short text left, long text right with bold phrases
  (on a phone, one column).
- **Strategic Partners**: the Emergence Growth and Bindura University logos, centred, with
  captions.
- **Capability Analysis** on charcoal: the four capabilities as a list, the image beside them
  (above them on a phone); **Value Driven and Capacity Building** with its heading on the right
  (on the left on a phone).
- **OUR LEADERSHIP**: eight people, four across, then two, then one; round photos; each bio cut
  after about nine lines with **Read more**. Press it: the whole bio shows and the button says
  **Show less**.

With JavaScript turned off (DevTools → Settings → Debugger → Disable JavaScript), reload.

**Expect:** every bio in full and no Read more buttons.

## 6. Edit About in the admin

Sign in at <http://localhost:8000/admin/>.

**Team → Team members:** eight people in order, with thumbnails. Change Florence Jambwa's order
from 80 to 5, **Save**, reload About.

**Expect:** Florence first. Set it back to 80.

Open **Farai Pilime**, put `linkedin.com/in/example` in **LinkedIn**, save, reload About.

**Expect:** a LinkedIn icon under Farai's bio, linking to `https://linkedin.com/in/example`. Clear
the field again.

**Pages → Partners and clients:** the two partners. **Pages → Pages → About Us → Sections:** six
sections; "Our Story" has its **Short text**; "Value Driven…" has **Heading position: Right**.

## 7. The CI checks

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
```

**Expect:** `All checks passed!`; `… files already formatted`; `0 errors, 0 warnings, 0 notes`;
`No changes detected`; `184 passed` with `Required test coverage of 85% reached`.

## 8. The image's static step and the deploy check

```bash
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e EMAIL_PROVIDER=console web python manage.py collectstatic --noinput --dry-run | tail -1
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e ALLOWED_HOSTS=example.org -e EMAIL_PROVIDER=console web python manage.py check --deploy
```

**Expect:** a file count with no `MissingFileError`, and
`System check identified no issues (2 silenced).`

## 9. Commit, push and open a PR

```bash
git add -A
git commit -m "Phase 1 Day 6: About, team, partners, seed part 2"
git push -u origin day-6
```

**Expect:** `test` and `css-fresh` both pass on the PR. Merge it.
