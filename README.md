# Distinctive Consultancy Services — website

The redesign of `distinctive.co.zw`, replacing the WordPress site. Django SSR, Postgres and
Docker, with Bootstrap and SCSS. The layering is Model → Repository → Service → Controller →
View (`docs/architecture.md`).

- **Phase 1** (current): Home, About, Services and Contact, admin-editable, live on the VPS.
- **Phase 2**: Jobs and site-wide Search.

Read `CLAUDE.md` first, then `docs/README.md`. After each completed day, run that day's
commands in `docs/commands/Phase_1/`.

## Local setup

Needs Docker (with Compose) and, from Day 2, Node 20+ for compiling SCSS on your machine.

```bash
cp .env.example .env            # then set SECRET_KEY
docker compose -f docker/docker-compose.yml up --build
```

Open <http://localhost:8000>. The health check is at <http://localhost:8000/healthz/>.

Always keep `--build`: the source is bind-mounted, but the Python packages live in the image.
If `requirements/` changed and the image wasn't rebuilt, the container stops and says so.

## Checks (the same as CI)

```bash
docker compose -f docker/docker-compose.yml exec web ruff check .
docker compose -f docker/docker-compose.yml exec web ruff format --check .
docker compose -f docker/docker-compose.yml exec web basedpyright
docker compose -f docker/docker-compose.yml exec web python manage.py makemigrations --check --dry-run
docker compose -f docker/docker-compose.yml exec web pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85
```

## Layout

See `docs/folder_structure.md`. In short: `apps/` (one folder per app, each with
`repositories/`, `services/`, `controllers/`, `tests/`), `config/settings/` (`base`, `dev`,
`test`, `prod`), `docker/`, `static/`, `templates/`, `docs/`.
