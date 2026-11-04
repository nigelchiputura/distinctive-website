# Phase 1 · Day 1: Project skeleton, settings, Docker, CI

**Cards:** `Phase_1/Task_Breakdown.md`, Day 1
**Completed:** 2026-11-03 · **Revised:** 2026-11-03 (Day 2): step 3, `SECRET_KEY` needs 50+ characters; the `check --deploy` in step 10 warns otherwise

Run from the repo root. Commands are bash; on Windows or macOS see
[`../Terminal_Note.md`](../Terminal_Note.md). Steps marked **ONE-TIME** are needed only the
first time; skip them on a later re-run.

## 1. Put the files in place (ONE-TIME)

Unzip `distinctive-site-day1.zip` where you keep your projects. It contains the folder
`distinctive-site/`.

```bash
unzip distinctive-site-day1.zip
cd distinctive-site
ls
```

```powershell
Expand-Archive distinctive-site-day1.zip .
cd distinctive-site
dir
```

**Expect:** `apps`, `config`, `docker`, `docs`, `requirements`, `static`, `templates`,
`CLAUDE.md`, `README.md`, `manage.py`, and the dotfiles (`.github`, `.env.example`,
`.gitignore`, `.dockerignore`, `.editorconfig`, `.coveragerc`).

## 2. Create the Git repository and push (ONE-TIME)

Create an empty **private** repository on GitHub first (no README, no .gitignore), then:

```bash
git init -b main
git add .
git commit -m "Phase 1 Day 1: project skeleton, settings, Docker, CI"
git remote add origin git@github.com:<you>/distinctive-site.git
git push -u origin main
```

**Expect:** the push succeeds, and the **CI** workflow starts under the repository's
**Actions** tab.

## 3. Environment file (ONE-TIME)

```bash
cp .env.example .env
```

```powershell
Copy-Item .env.example .env
```

Generate a key and paste it into `.env` as `SECRET_KEY` (50+ characters; a shorter one makes
`check --deploy` warn in step 10). Leave the rest as is.

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

**Expect:** `.env` exists and is **not** listed by `git status` (it's ignored).

## 4. Build and start

```bash
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml logs -f web
```

**Expect:** `Database is ready.`, then the migrations applying (`Applying users.0001_initial…
OK` before `Applying admin.0001_initial… OK`), then
`Starting development server at http://0.0.0.0:8000/`. Press Ctrl+C to stop following the log;
the app keeps running.

## 5. Look at it

Open <http://localhost:8000> and <http://localhost:8000/healthz/>.

**Expect:** the placeholder page "Distinctive Consultancy Services … Phase 1, Day 1", and
`{"db": "ok"}` from the health check.

## 6. Check the migration order

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py showmigrations --plan | grep -E "users|admin.0001"
```

**Expect:** `[X]  users.0001_initial` on the line **above** `[X]  admin.0001_initial`.

## 7. Create a superuser and sign in to the admin

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py createsuperuser
```

It asks for an email address, a username and a password (12 characters or more).

**Expect:** `Superuser created successfully.` Then sign in at <http://localhost:8000/admin/>
with the email and password, and see **Users** listed.

## 8. Data survives a restart

```bash
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml up --build -d
```

**Expect:** the superuser from step 7 still signs in. (`down` keeps the `pg_data` volume. Only
`down -v` deletes it, so never add `-v` unless you mean to wipe your local database.)

## 9. The checks CI runs, inside the container

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
```

**Expect:** `All checks passed!`; `… files already formatted`; `0 errors, 0 warnings, 0 notes`;
`No changes detected`; `10 passed` with `Required test coverage of 85% reached`.

## 10. The production settings and the image's static step

```bash
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e SECRET_KEY=build-only web python manage.py collectstatic --noinput --dry-run
docker compose -f docker/docker-compose.yml exec -e DJANGO_SETTINGS_MODULE=config.settings.prod -e ALLOWED_HOSTS=example.org web python manage.py check --deploy
```

**Expect:** a count of static files that would be copied, and
`System check identified no issues (2 silenced).` The two silenced checks (HSTS for
subdomains, and preload) are deliberate (`deployment.md` §7).

## 11. The stale-image guard (optional)

```bash
echo "# test" >> requirements/dev.txt
docker compose -f docker/docker-compose.yml restart web
docker compose -f docker/docker-compose.yml logs --tail 3 web
git checkout requirements/dev.txt
docker compose -f docker/docker-compose.yml up --build -d
```

**Expect:** after the restart, `ERROR: requirements/ has changed since this image was built.`
and the rebuild command. After `git checkout` and `up --build`, the app runs again.

## 12. CI on GitHub

Open the repository's **Actions** tab, then the run from step 2.

**Expect:** both jobs green. `test` runs ruff, basedpyright, the migrations check and pytest on
Postgres; `css-fresh` reports there's no npm pipeline yet and passes (it checks the CSS from
Day 2).

## 13. Protect `main` (ONE-TIME, GitHub settings)

**Settings → Branches → Add branch protection rule** (or **Rulesets**) for `main`: require a pull
request before merging, and require the status checks `test` and `css-fresh` to pass.

**Expect:** from Day 2, work goes through a branch and a PR, and GitHub blocks the merge until
both checks are green.
