# Phase 1 · Day 9: UI and components polish (light and dark themes, modern components, motion)

**Cards:** `Phase_1/Task_Breakdown.md`, Day 9 (added 2026-11-04; SEO moved to Day 10, go-live to
Day 11)
**Completed:** 2026-11-04 · **Revised:** 2026-11-04 (the team photo behind Home's hero; the
gradient on the other heroes and the Contact band)

Run from the repo root. Commands are bash; on Windows or macOS see
[`../Terminal_Note.md`](../Terminal_Note.md).

**This zip also contains Day 10 work started early:** the SEO service and `_seo.html`, the
`pages.Redirect` model, middleware and `check_redirects` command, the 404 and 500 pages, and the
production files (`docker/docker-compose.prod.yml`, `docker/Caddyfile`, `.env.prod.example`,
`.github/workflows/deploy-vps.yml`, CI's `build-and-push` job). Its tests run in step 9 below.
Day 10's commands file covers checking it in full.

## 1. Put the files in place

```bash
git checkout main && git pull
git checkout -b day-9
unzip -o ../distinctive-site-day9.zip -d ..
# Unzipping can't delete: the Read more script was replaced by the bio dialog.
git rm -q static/js/modules/read-more.js
git status --short | head -80
```

```powershell
git checkout main; git pull
git checkout -b day-9
Expand-Archive -Force ..\distinctive-site-day9.zip ..
git rm -q static/js/modules/read-more.js
git status --short
```

**Expect:**

- **New:**
  - `static/scss/_theme.scss`, `static/js/theme-init.js`, and the modules `theme.js`, `reveal.js`, `navbar.js`, `bio-dialog.js` and `back-to-top.js`.
  - `templates/includes/_theme_toggle.html`, `_section_head.html` and `_contact_list.html`.
  - `static/img/logo-dark.png`, nine new icons in `templates/includes/icons/`, and the team
    photo `apps/core/seed/images/team-photo.jpg`.
  - The migration `pages/0008_section_label.py` and `apps/core/tests/test_polish.py`.
  - Day 10's early files (listed above), including migrations `0006` and `0007`.
- **Changed:** nearly every SCSS partial and template, both compiled CSS files, `main.js`, `contact-form.js`, `scripts/copy-vendor.mjs`, the seed, and the docs.
- **Deleted (shown as `D`):** `read-more.js`.

## 2. Icons and the CSS

```bash
npm ci
npm run vendor
npm run build:css
git status --short static/ templates/includes/icons/
```

**Expect:** `npm run vendor` lists 17 `wrote templates/includes/icons/…` lines. `git status` then
shows nothing new: the committed icons and CSS are what the packages produce, and the build
prints no warnings.

## 3. Start and migrate

```bash
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml logs --tail 20 web
```

**Expect:** `Applying pages.0006_redirects… OK`, `Applying pages.0007_search_title_help… OK`,
`Applying pages.0008_section_label… OK`, then the development server starting.

## 4. Load the new content

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
docker compose -f docker/docker-compose.yml exec web python manage.py seed_site_content
```

**Expect:** on a database seeded on Days 5–8, the first run prints
`Added 1 section, 9 redirects. Filled in empty fields on 17 existing item(s).` These are:
- the section: Contact's page hero;
- the redirects: Day 10's early work;
- the 17 items: each section's label, Home's "What We Do" heading, and the team photo on Home's
  hero slide (copied into the media volume as `pages/slides/team-photo.jpg`).

The second run prints `Nothing to add: the content is already there.`

## 5. The look, in the light theme

Set your computer to its light appearance. Open <http://localhost:8000/>, then About, Services
and Contact, at full width and at phone width (375 px).

**Expect:**

- **Home:**
  - The team photo behind the hero, with the gold heading and tagline over the trees and every
    face clear (check at phone, tablet and full width).
  - "OUR SERVICES · What We Do", with six frosted cards. Each lifts with a gold edge on hover, its image zooms slightly, and "Learn more →" nudges right.
  - The "Let's talk" panel with a filled gold button.
  - People Centred and Proactive with framed photos.
- **About, Services and Contact:** the page hero on the drifting black-and-gold gradient (gold
  light moving slowly across black), the same on Contact's form band.
- **About:**
  - Our Story's long text in a frosted card on the blue band.
  - Partner logos on white tiles.
  - Team cards with gold photo rings, with bios cut to five lines and **Read full bio**.
- **Services:**
  - Numbered chips (`01`–`13`) linking to numbered bands.
  - Ten client logos, five and five.
  - The gold enquiry band with the form in a white card.
- **Contact:**
  - The "Contact Us" page hero.
  - The form in a frosted card beside a gold-edged Reach Us card with icons.
  - The "Find Us" card beside the map frame.
- **Every page:**
  - Sections fade up as you scroll.
  - The navbar gains a shadow once you scroll.
  - A round gold ↑ button appears bottom right.
  - A three-column footer.

## 6. Themes

Click the round button at the right of the navbar (half-filled circle).

**Expect:** a menu with **System** (ticked), **Light** and **Dark**. Choose **Dark**: the page,
cards and text switch at once, and the navbar logo turns light. Reload: still dark, with no flash
of white first. Choose **System**, then set your computer to dark: the site follows it without a
reload. DevTools → Application → Local Storage shows `dcs-theme: dark` while Dark is chosen and
nothing once System is.

With JavaScript off (DevTools → ⋮ → Run command → "Disable JavaScript"), reload.

**Expect:** the toggle and the cookie card are gone, the site follows the system setting, every
section and card is visible (nothing waits to fade in), every bio shows in full, and the ↑ link
is always there and jumps to the top. Turn JavaScript back on.

## 7. The bio dialog, back to top and reduced motion

On About, press **Read full bio** under Rose Nhamo.

**Expect:** the dialog opens with her photo, name, title and whole bio over a blurred page, and
focus on the × button. Escape closes it, as do the × and a click outside, and focus returns to
the button. Tab to a card's button and press Enter: the same.

Scroll down any page, then press the ↑ button (or Tab to it and press Enter).

**Expect:** a smooth scroll to the top, with focus on the logo.

Turn on reduced motion: DevTools → ⋮ → Run command → "Emulate CSS prefers-reduced-motion:
reduce". Reload Home.

**Expect:** no fading in, no drifting light on the gradients, and every card shown at once. ↑ jumps rather than
scrolls.

## 8. Day 8's features still work

Repeat Day 8's step 5 (the Contact form with errors, then a sent message), step 6's Services
enquiry, and step 8's cookie check with the placeholder `GA_MEASUREMENT_ID` and
`GOOGLE_MAPS_EMBED_KEY`.

**Expect:** the same results as on Day 8, in the new look: errors under each field, the
thank-you with a tick, the cookie card bottom left, and no request to Google before **Accept**.
On a phone the ↑ button waits until the cookie card is answered.

## 9. The CI checks

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
```

**Expect:**
- `ruff check .`: `All checks passed!`
- `ruff format --check .`: `… files already formatted`
- `basedpyright`: `0 errors, 0 warnings, 0 notes`
- `makemigrations --check`: `No changes detected`
- `pytest`: `296 passed` with `Required test coverage of 85% reached`

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
git commit -m "Phase 1 Day 9: UI and components polish (themes, components, motion, back to top)"
git push -u origin day-9
```

**Expect:** `test` and `css-fresh` both pass on the PR. Merge it.
