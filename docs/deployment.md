# Deployment Plan

**Project-wide · revised 2026-11-02:** Phase 1 goes **live on a VPS** at `distinctive.co.zw` (no
Render demo); email through **Resend's HTTPS API** (replacing Brevo); uploaded media in a
**Docker volume** served by Caddy (Cloudflare R2 deferred to the backlog).

One application image for every environment. Only environment variables and what starts the
container differ. The pipeline is the one proven on Consult 360: GitHub Actions → GHCR → a manual
deploy to a VPS running Docker Compose with Caddy.

## 1. Environments

| Environment | Where | Purpose | When |
|---|---|---|---|
| Local | Docker Compose on the developer machine (plus Node for SCSS, on the machine only) | Development | Phase 1 Day 1 |
| CI | GitHub Actions | Lint, type check, tests, CSS freshness, image build | Phase 1 Day 1 |
| Local prod stack | `docker-compose.prod.yml` on the developer machine | Prove the production files before the VPS | Phase 1 Day 9 |
| Preview | The VPS at `new.distinctive.co.zw` | Client walkthrough before cutover | Phase 1 Day 10 |
| Production | The same VPS at `distinctive.co.zw` | The live site | Phase 1 Day 10, after sign-off |

The preview is the production server under a second hostname, not a separate environment. After
cutover, `new.` redirects to the live domain (or is removed).

## 2. The Docker image

```dockerfile
# docker/Dockerfile

# ---- Stage 1: build ----
FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# prod.txt for the pushed image; docker-compose passes REQUIREMENTS=dev.txt for local dev.
ARG REQUIREMENTS=prod.txt
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/${REQUIREMENTS} \
    && sha256sum requirements/*.txt > /requirements.sha256
COPY . .
# static/css/main.css is already compiled and committed. No Node, no Sass here.
# A dummy DATABASE_URL: settings require one, collectstatic never connects.
RUN DJANGO_SETTINGS_MODULE=config.settings.prod SECRET_KEY=build-only \
    DATABASE_URL=postgres://build:build@localhost:5432/build \
    python manage.py collectstatic --noinput

# ---- Stage 2: runtime ----
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* && useradd --create-home --uid 1000 appuser
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
# Fingerprint of requirements/ at build time; entrypoint.sh refuses to start on a stale image.
COPY --from=builder /requirements.sha256 /requirements.sha256
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && mkdir -p /app/media && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

**Two variants, one Dockerfile.** CI and the pushed image use the default `prod.txt`.
`docker/docker-compose.yml` builds with `REQUIREMENTS: dev.txt` (which includes `prod.txt`,
because the build's `collectstatic` runs with prod settings and needs WhiteNoise), so `pytest`,
`ruff` and `basedpyright` run inside the local container. basedpyright bundles a Node runtime in
site-packages, so the dev image contains one; the shipped image does not.

**`/app/media` is owned by `appuser` in the image.** When an empty named volume is first mounted
there, Docker copies that ownership into it, so uploads work without a `chown` at start-up.

**Locally, always `up --build`.** Compose bind-mounts the source over `/app`, but the Python
packages are frozen in the image; a stale image runs new code against old packages.

**Fast local check before a full image build.** WhiteNoise's manifest storage (prod only) rejects
any `url()` in CSS that points at a missing file. Run the same step the Dockerfile runs whenever a
vendored asset changes:

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod SECRET_KEY=build-only python manage.py collectstatic --noinput
```

### 2.1 Entrypoint

`docker/entrypoint.sh`:

1. Checks that `requirements/` still matches the build-time fingerprint. If not (a stale local
   image under the bind mount), it stops with "requirements/ has changed since this image was
   built" and the rebuild command. In the pushed image the source is baked in, so it always
   passes.
2. Waits up to 30 seconds for Postgres, using the app's own `DATABASE_URL`.
3. Runs `migrate --noinput` (this also prints the `core.W00x` checks into the logs) and, from
   Day 8, `createcachetable` (the rate limiter's shared cache).
4. Runs `seed_site_content` when `SEED_SITE_CONTENT=true` (first deploy only; it's idempotent).
5. `exec "$@"`: gunicorn in the image, `runserver` under docker-compose.

Phase 2 adds `rebuild_search_index` after step 4.

## 3. Environment variables

| Variable | Local (`.env`) | VPS (`.env`) |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` | `config.settings.prod` |
| `SECRET_KEY` | any | generated, 50+ characters |
| `DATABASE_URL` | the compose `db` service | built from `POSTGRES_*` in the compose file |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | set | set (strong password) |
| `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` | `localhost` | the preview host, then the live domain and `www` |
| `SITE_DOMAIN` | — | `new.distinctive.co.zw`, then `distinctive.co.zw` (Caddy and canonical URLs) |
| `SITE_URL` | `http://localhost:8000` | `https://<SITE_DOMAIN>` (canonical URLs, sitemap, emails) |
| `GHCR_IMAGE`, `IMAGE_TAG` | — | `owner/repo` in lower case; `latest` or a commit SHA |
| `ADMIN_URL_PATH` | `admin/` | something not guessable, ending in `/` |
| `EMAIL_PROVIDER` | `console` (prints emails); `resend` to send for real while testing | `resend` |
| `RESEND_API_KEY` | only with `resend` | Resend **Sending access** key, limited to the sending domain |
| `DEFAULT_FROM_EMAIL` | `Distinctive Website <website@website.localhost>` (fine with `console`) | **required:** a sender on the verified domain, e.g. `Distinctive Website <website@mail.distinctive.co.zw>` |
| `CONTACT_RECIPIENT` | your own inbox | `enquiries@distinctive.co.zw` |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | — | only with `EMAIL_PROVIDER=smtp` (fallback, §6) |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | the OAuth client | the same client (redirect URIs registered for each host) |
| `GA_MEASUREMENT_ID` | empty (no analytics locally) | `G-…` (can also be set in `SiteSettings`) |
| `GOOGLE_MAPS_EMBED_KEY` | a key allowing `localhost` | the referrer-restricted key |
| `SEED_SITE_CONTENT` | `true` (optional) | `true` on the first deploy only, then removed |
| `SECURE_SSL_REDIRECT` | — | `true` (default) |

`.env.example` and `.env.prod.example` list every variable with placeholders. Real values never
go into the repo.

## 4. Local development (Docker Compose)

```yaml
# docker/docker-compose.yml
services:
  web:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      args: { REQUIREMENTS: dev.txt }
    command: python manage.py runserver 0.0.0.0:8000
    env_file: ../.env
    volumes:
      - ..:/app
      - media_data:/app/media
    depends_on: [db]
    ports: ["8000:8000"]
  db:
    image: postgres:16
    env_file: ../.env
    volumes:
      - pg_data:/var/lib/postgresql/data
volumes:
  pg_data:
  media_data:
```

SCSS is compiled on the host: `npm run build:css`, or `npm run watch:css` while styling. The
bind mount means a recompiled `static/css/main.css` shows up immediately.

## 5. CI/CD

```mermaid
flowchart LR
    A[Push / PR] --> T[test\nruff + basedpyright + makemigrations --check\n+ pytest with Postgres]
    A --> C[css-fresh\nnpm ci, build:css,\ngit diff --exit-code]
    T --> G{both pass?}
    C --> G
    G -- no --> X[Block merge]
    G -- yes, main only --> B[build-and-push\nimage → GHCR :sha, :latest]
    B -. manual .-> V[Deploy VPS workflow\nSSH: compose pull web + up -d]
```

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_USER: dcs, POSTGRES_PASSWORD: dcs, POSTGRES_DB: dcs_test }
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U dcs" --health-interval 5s --health-retries 10
    env:
      DJANGO_SETTINGS_MODULE: config.settings.test
      SECRET_KEY: ci-only
      DATABASE_URL: postgres://dcs:dcs@localhost:5432/dcs_test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip, cache-dependency-path: requirements/*.txt }
      - run: pip install -r requirements/dev.txt
      - run: ruff check .
      - run: ruff format --check .
      - run: basedpyright
      - run: python manage.py makemigrations --check --dry-run
      - run: pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85

  css-fresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run build:css
      - name: Compiled CSS must match the committed file
        run: git diff --exit-code -- static/css/
      - name: No source-map references may ship
        run: "! grep -q 'sourceMappingURL' static/css/*.css static/vendor/bootstrap/bootstrap.bundle.min.js"

  build-and-push:
    needs: [test, css-fresh]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write }
    steps:
      - uses: actions/checkout@v4
      - name: Image name must be lower case for GHCR
        run: echo "IMAGE=ghcr.io/${GITHUB_REPOSITORY,,}" >> "$GITHUB_ENV"
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }
      - uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/Dockerfile
          push: true
          tags: |
            ${{ env.IMAGE }}:latest
            ${{ env.IMAGE }}:${{ github.sha }}
```

**Why this shape:**

- **`makemigrations --check`** fails CI if a model changed without a committed migration.
- **Nothing builds unless both gates pass.** The tests prove the logic; `css-fresh` proves the
  shipped CSS is what the SCSS says.
- **Branch protection** on `main` requires `test` and `css-fresh`, so the gate is a rule, not a
  habit.
- **Images are tagged by commit SHA,** so every running container traces to a commit and a bad
  release rolls back to an earlier SHA.
- **Production deploys are a conscious action** (the manual workflow, §7), not automatic on
  push. With no demo environment, `main` passing CI is not the same as "ready for the client".

## 6. Email — Resend

Email goes through **Resend's HTTPS API** (port 443) using `django-anymail`, the same setup as
Consult 360 and CVision. Why:

- **No SMTP ports.** Many VPS providers block outbound SMTP for new accounts, and Render's free
  plan blocks it outright (the error that moved Consult 360 to Resend). An HTTPS API works
  anywhere the app can reach the web.
- **The provider is a setting.** `EMAIL_PROVIDER` (`resend`, `smtp` or `console`) picks
  `EMAIL_BACKEND` in `config/settings/email.py` (default `console` locally, `resend` with prod
  settings); any other value stops start-up with `ImproperlyConfigured`. Changing provider
  later is a setting and a key, not a code change. `smtp` stays available as a fallback (for
  example Google Workspace's `smtp.gmail.com:587` with an app password, if the VPS allows it).

**One-time setup (owner):**

1. In the existing Resend account, add a **sending subdomain** of the client's domain, for
   example `mail.distinctive.co.zw` (Resend recommends a subdomain; CVision may already have
   added one, in which case the website reuses it).
2. Add its DNS records at the domain's DNS host (Cloudflare, per the CVision notes; confirm): an
   MX and a TXT record for `send.mail`, a DKIM TXT record, and a DMARC TXT record
   (`v=DMARC1; p=none;` to start) if the domain has none. These are new subdomain records; they
   **don't touch the root domain's MX**, so the existing `enquiries@` mailbox is unaffected.
3. An API key with **Sending access** only, limited to that domain, in `RESEND_API_KEY`.
4. `DEFAULT_FROM_EMAIL` on the verified domain; `CONTACT_RECIPIENT=enquiries@distinctive.co.zw`.

**What is sent.** One notification per enquiry to `CONTACT_RECIPIENT`, with the visitor's
address as `Reply-To` (replying in the mailbox answers the visitor), the source page in the
subject, and the message as plain text. Allauth's set-password and reset emails use the same
backend.

**Misconfiguration is loud** (learned on Consult 360, where the demo silently sent from
`noreply@localhost`):

- `apps/core/checks.py` warns at every start whenever the provider isn't `console`, from
  `migrate` in the entrypoint, so it lands in the container logs: **W001** the sender isn't on a real domain (`localhost`, `example.*`, or
  empty); **W002** Resend without a key; **W003** SMTP without a login.
- `LOGGING` in `base.py` sends warnings and errors to the container output. Without it, Django
  logs almost nothing with `DEBUG` off.
- `ContactService` logs each failed send with the provider's message and stores it on the
  submission.

**Failure handling.** `ContactService.submit` saves first and never raises a send failure to the
visitor. A failed send leaves `email_sent=False` and `email_error` set; the admin action
**Resend notification email** retries it once the cause is fixed.

**Limits.** Resend's free plan (checked 2026-10-19 for Consult 360): 100 emails a day, 3,000 a
month, 3 domains, **per account**. The website shares the account with CVision, so their volumes
add up. A brochure site's enquiries are far below this, but check the dashboard if CVision sends
in bulk; Pro is $20 a month.

**Data.** Enquiries carry a name, an email address and a message. Resend is a US company
(sending through Amazon SES). The same Zimbabwean data protection question raised for
Consult 360 applies, in a much smaller form: note it for the client; Brevo (EU) remains a
drop-in alternative through anymail.

## 7. Production — VPS

**Which VPS:** the comparison in Consult 360's `deployment.md` §9 applies. For a public brochure
site the data-residency concern is much smaller (no staff data; only enquiries), so its
recommendation, **Vultr Johannesburg, 1 vCPU / 2 GB / 55 GB with backups (about $12/month)**, is
the default (`Phase_1/Phase1_Scope.md` Q2). The website could also share a server with another
of the owner's apps; it needs about 250 MB of RAM for three gunicorn workers plus Postgres.

**Server set-up (once):** Ubuntu 24.04 LTS; a non-root `deploy` user in the `docker` group; SSH
keys only (password login and root login off); `ufw` allowing 22, 80 and 443; Docker Engine and
the Compose plugin; the app folder `/srv/distinctive` holding `docker-compose.prod.yml`,
`Caddyfile` and `.env`.

```yaml
# docker/docker-compose.prod.yml
services:
  web:
    image: ghcr.io/${GHCR_IMAGE:?set GHCR_IMAGE}:${IMAGE_TAG:-latest}
    restart: unless-stopped
    env_file: .env
    environment:
      DATABASE_URL: postgres://${POSTGRES_USER:?}:${POSTGRES_PASSWORD:?}@db:5432/${POSTGRES_DB:?}
    volumes:
      - media_data:/app/media
    depends_on:
      db: { condition: service_healthy }
    expose: ["8000"]
  db:
    image: postgres:16
    restart: unless-stopped
    env_file: .env
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER}"]
      interval: 5s
      retries: 10
  caddy:
    image: caddy:2
    restart: unless-stopped
    environment:
      SITE_DOMAIN: ${SITE_DOMAIN:?set SITE_DOMAIN}
    ports: ["80:80", "443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - media_data:/srv/media:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on: [web]
volumes:
  pg_data:
  media_data:
  caddy_data:
  caddy_config:
```

```
# docker/Caddyfile
{$SITE_DOMAIN} {
    encode zstd gzip
    header -Server

    # Admin-uploaded images, straight from the media volume
    handle_path /media/* {
        root * /srv/media
        file_server
        header Cache-Control "public, max-age=604800"
    }

    handle {
        reverse_proxy web:8000
    }
}

# Added at cutover (§8): redirect www and the preview host to the live domain
# www.distinctive.co.zw, new.distinctive.co.zw {
#     redir https://distinctive.co.zw{uri} permanent
# }
```

- **Caddy** gets and renews certificates, redirects HTTP to HTTPS and serves `/media/` from the
  volume read-only. Keep `caddy_data`: it holds the certificates.
- **Static files** (CSS, JS, vendor assets) are served by WhiteNoise from the image, with
  long-lived hashed URLs.
- **Compose, not Kubernetes:** one web container doesn't justify a cluster.
- **`restart: unless-stopped`** survives reboots.

**Deploy** with `.github/workflows/deploy-vps.yml` (Actions → **Deploy VPS** → **Run
workflow**). It SSHes in and runs `docker compose -f docker-compose.prod.yml pull web` and
`up -d --remove-orphans`. Secrets: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_APP_DIR`; it uses
a GitHub environment named `production`. To **roll back**, run it with `image_tag` set to an
earlier commit SHA.

**Backups:** a nightly cron on the server runs `pg_dump` from the `db` container and archives
the `media_data` volume (`tar` through a throwaway container) into `/srv/backups`, keeps 14 days,
and copies them off the server (Backblaze B2's free 10 GB, as recommended for Consult 360, or the
VPS provider's own backups). **Both** are needed: the database holds the content, the volume
holds the images. Test a restore once on Day 10.

**Security settings.** `config/settings/prod.py`: `DEBUG = False`, secure and HttpOnly session
cookies, a secure CSRF cookie (readable by `http.js`, so not HttpOnly), the HTTPS redirect,
`SECURE_PROXY_SSL_HEADER` for Caddy, `nosniff`, `X-Frame-Options: DENY`, a strict referrer
policy, and HSTS starting at one week (raise to a year once the domain has been stable for a
while). HSTS for subdomains and preload stay off on purpose: other `distinctive.co.zw`
subdomains (mail, the old host's webmail) aren't ours to force onto HTTPS, and preload is hard to
undo. Their two checks (`security.W005`, `W021`) are silenced in `prod.py`, so
`python manage.py check --deploy` must print no issues apart from those two silenced ones;
`apps/core/tests/test_security.py` runs it in CI.

## 8. Go-live: preview and cutover (Phase 1 Day 10)

**Before the day:**

- Take a full backup of the WordPress site (files and database) off the old host.
- Export the old site's URL list (`/wp-sitemap.xml` or `/sitemap_index.xml`) for the redirect
  seed.
- Note every current DNS record for `distinctive.co.zw`, especially **MX, SPF (TXT), DKIM and
  any `mail`/`webmail`/`autodiscover` records**. These stay exactly as they are.
- Lower the TTL of the apex `A`/`AAAA` and `www` records to 300 seconds at least a day before.

**Preview:**

1. Add `new.distinctive.co.zw` → the VPS's IP (an `A` record; DNS only, not proxied, if the DNS
   host is Cloudflare, so Caddy can get its certificate).
2. `.env`: `SITE_DOMAIN=new.distinctive.co.zw`, `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` for
   it, `SEED_SITE_CONTENT=true`.
3. Run the **Deploy VPS** workflow. Check the logs for the migrations, the seed and no `core.W00x`
   warnings.
4. Create the client's users (`onboard_user`), then remove `SEED_SITE_CONTENT` from `.env`.
5. Submit an enquiry: it arrives in the mailbox and the admin shows **Email sent: Yes**.
6. Walk the client through it (`Phase_1/Test_Plan.md` §4).

**Cutover (after sign-off):**

1. `.env`: `SITE_DOMAIN=distinctive.co.zw`; add `distinctive.co.zw`, `www.distinctive.co.zw` to
   `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`; `SITE_URL=https://distinctive.co.zw`.
2. Uncomment the redirect block in the `Caddyfile`.
3. Change the apex `A`/`AAAA` and the `www` record to the VPS. **Change nothing else.**
4. `docker compose -f docker-compose.prod.yml up -d`; watch `docker compose logs caddy` for
   the new certificates.
5. Check: the live domain over HTTPS; `www` and `new.` redirect to it; the old sitemap's URLs
   answer 301; an email to `enquiries@` still arrives; Google sign-in works (the live redirect
   URI is registered).
6. Update the Google Maps key's referrers and the GA4 property's URL if needed; submit the new
   sitemap in Google Search Console.

**Rollback during the cutover window:** point the apex and `www` records back at the old host.
The WordPress site is untouched until the client is happy, so this is a DNS change only.

## 9. Deliberately not done yet

- Zero-downtime deploys (a brief restart on `up -d` is acceptable for a brochure site).
- A separate staging server (the preview hostname serves that purpose at go-live).
- Object storage or a CDN for media (Cloudflare R2 is in the backlog, `Phase_2/Phase2_Scope.md`
  §6).
- A secrets manager (GitHub secrets and the server `.env` are enough at this scale).
- Background workers (one email per enquiry sends in-request in well under a second).
