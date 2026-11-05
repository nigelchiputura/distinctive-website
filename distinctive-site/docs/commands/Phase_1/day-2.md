# Phase 1 · Day 2: Sass pipeline, brand tokens, header and footer

**Cards:** `Phase_1/Task_Breakdown.md`, Day 2
**Completed:** 2026-11-03 · **Revised:** —

Run from the repo root. Commands are bash; on Windows or macOS see
[`../Terminal_Note.md`](../Terminal_Note.md). Steps marked **ONE-TIME** are needed only the
first time.

## 1. Put the files in place

Work on a branch (branch protection on `main` needs a PR). Unzip `distinctive-site-day2.zip`
**over** your repo; it contains the whole project, so new and changed files replace the old ones.

```bash
git checkout -b day-2
unzip -o ../distinctive-site-day2.zip -d ..
git status --short | head -30
```

```powershell
git checkout -b day-2
Expand-Archive -Force ..\distinctive-site-day2.zip ..
git status --short
```

**Expect:** new `package.json`, `package-lock.json`, `scripts/`, `static/scss/`,
`static/css/main.css`, `static/vendor/`, `static/img/logo.png`, `templates/`, three new
`apps/core` files and their tests, a new folder in `docs/errors-and-exceptions/`, and changed
docs. Nothing under `requirements/` changed.

## 2. `SECRET_KEY` length (ONE-TIME, if yours is short)

`check --deploy` (step 8) warns about a key under 50 characters. If the one in your `.env` is
shorter, generate a new one and replace it:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

**Expect:** a 67-character string. Paste it into `.env` as `SECRET_KEY=…`.

## 3. Node (ONE-TIME)

Install **Node 22 LTS** or later from <https://nodejs.org> (on your machine only; it never goes
into the image or onto a server). Node 20 reached end of life in April 2026.

```bash
node --version
```

**Expect:** `v22.x` or higher.

## 4. Install the npm packages and compile the CSS

```bash
npm ci
npm run build:css
git status --short static/css/
```

**Expect:** `added … packages`, then the build with **no warnings**, then **nothing** from
`git status` (the committed `main.css` is already what the SCSS compiles to).

## 5. Vendored files are up to date

```bash
npm run vendor
git status --short static/vendor templates/includes/icons
```

**Expect:** `copied static/vendor/bootstrap/bootstrap.bundle.min.js (source-map reference
removed)`, the Open Sans fonts and eight icons, then **nothing** from `git status`.

## 6. Start the app

```bash
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml logs --tail 5 web
```

**Expect:** `Starting development server at http://0.0.0.0:8000/`. (No requirements changed,
but keep `--build` as a habit.)

## 7. Look at the layout at three widths

Open <http://localhost:8000>, then open the browser's device toolbar (F12, then Ctrl+Shift+M;
Cmd+Shift+M on a Mac) and check 1280, 768 and 375 px wide.

**Expect:**

- a black top bar with the phone number and email (icons only at 375 px);
- the white navbar with the logo, and **Home** in dark gold with a gold underline;
- below 992 px, a menu button that opens the four links;
- a charcoal placeholder band ("Home arrives on Day 5");
- the footer: "Reach Us" in gold with the address, phone, hours and email; a dark strip with the
  four links in gold; the copyright line;
- no sideways scrolling at any width;
- pressing **Tab** once after loading shows a gold "Skip to content" button at the top left.

No social icons appear yet: their URLs are empty until the client confirms them (Day 3 makes
them editable).

## 8. The image's static step and the deploy check

```bash
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod web python manage.py collectstatic --noinput --dry-run
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e ALLOWED_HOSTS=example.org web python manage.py check --deploy
```

**Expect:** a count of files with no `MissingFileError` (the vendored Bootstrap bundle no
longer points at a missing `.map`), and `System check identified no issues (2 silenced).`

## 9. The checks CI runs

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
```

**Expect:** `All checks passed!`; `… files already formatted`; `0 errors, 0 warnings, 0 notes`;
`No changes detected`; `28 passed` with `Required test coverage of 85% reached`.

## 10. Commit, push and open a PR

```bash
git add -A
git commit -m "Phase 1 Day 2: Sass pipeline, brand tokens, header and footer"
git push -u origin day-2
```

Open the pull request on GitHub.

**Expect:** both checks, `test` and `css-fresh`, run on the PR and pass. Merge it.

## 11. Prove `css-fresh` catches stale CSS (optional)

On a throwaway branch, change an SCSS value without rebuilding, and push. (On Windows without
Git Bash, make the `sed` change by hand: in `static/scss/_tokens.scss`, change `#d4af37` to
`#d4af38` on the `$dcs-gold` line.)

```bash
git checkout -b css-fresh-check
sed -i 's/\$dcs-gold: #d4af37;/$dcs-gold: #d4af38;/' static/scss/_tokens.scss
git commit -am "Check that css-fresh fails on stale CSS"
git push -u origin css-fresh-check
```

Open a PR from it.

**Expect:** `css-fresh` **fails** at "Compiled CSS must match the committed file". Close the PR
without merging, then clean up:

```bash
git checkout main && git pull
git branch -D css-fresh-check && git push origin --delete css-fresh-check
```
