# Phase 1 — Task Breakdown (10 working days)

Day-by-day cards, ready to paste into GitHub issues (`Backlog` → `In Progress` → `In Review` →
`Done`). Each card is **Title** — what to do — **AC** (acceptance criteria). Scope and decisions:
`Phase_1/Phase1_Scope.md`.

**Standing practices, every day:**

- Work in a branch, open a PR, merge only when CI is green.
- Any non-trivial error gets an entry in `docs/errors-and-exceptions/`
  (`Errors_And_Exceptions.md` §7). It's part of finishing the card the bug interrupted.
- Any commit touching `static/scss/` runs `npm run build:css` first (`frontend.md` §1). CI's
  `css-fresh` job enforces it.
- Every new service gets fake-repository tests the same day; every new route gets a smoke test
  (`Testing_Strategy.md`).
- File locations follow `folder_structure.md`. Commands run from the repo root.
- **No Jobs or Search code** (Phase 2).

A day ends with its **Definition of Done**. If it isn't met, don't start the next day's
critical-path cards. A day also isn't done until `commands/Phase_1/day-N.md` is written
(`Development_Conventions.md` §3.2).

---

## Day 1 — Environment and project skeleton

**Goal:** `docker compose up --build` serves Django backed by Postgres, and CI is green.

- [x] **Repository and settings.** Repo layout from `folder_structure.md` §1; `config/settings/
  {base,dev,test,prod}.py` with `django-environ`; `.env.example`; `.gitignore`;
  `.dockerignore`; `.editorconfig`; `README.md` with local setup.
  AC: `python manage.py check` passes with `config.settings.dev`.
- [x] **Requirements.** `requirements/base.txt` → `prod.txt` (includes base; gunicorn,
  whitenoise) → `dev.txt` (includes prod; pytest, pytest-django, pytest-cov, ruff,
  basedpyright, django-stubs).
  AC: each file `-r`-includes the one before.
- [x] **Apps scaffolded.** `apps/core`, `apps/users`, `apps/pages`, `apps/offerings`,
  `apps/team`, `apps/contact`, each with `repositories/`, `services/`, `controllers/`,
  `tests/`. Not `jobs` or `search` (Phase 2).
  AC: all apps registered; `check` passes.
- [x] **Custom user first.** `apps/users/models.py` with `User(AbstractUser)` (fields only;
  allauth on Day 4), `AUTH_USER_MODEL = "users.User"`, and its `0001` migration **before any
  other app's migration** (`users.md` §1).
  AC: `showmigrations` lists `users.0001` before `admin.0001`.
- [ ] **Docker.** *(files done and checked outside Docker on 2026-11-03; owner confirms with `commands/Phase_1/day-1.md` steps 4–6)* `docker/Dockerfile` (multi-stage, non-root, `REQUIREMENTS` build arg,
  requirements fingerprint), `docker/entrypoint.sh` (fingerprint check, wait for Postgres,
  `migrate`, optional seed, then `exec "$@"`), `docker/docker-compose.yml` (`web` with
  `REQUIREMENTS: dev.txt`, `db` postgres:16; volumes `pg_data`, `media_data`).
  AC: `docker compose -f docker/docker-compose.yml up --build` prints `Database is ready.`, the
  migrations, then `runserver`'s start line; `/admin/` loads.
- [ ] **Persistence check.** *(files done and checked outside Docker on 2026-11-03; owner confirms with `commands/Phase_1/day-1.md` steps 7–8)* Create a superuser, `down` (no `-v`), `up --build` again.
  AC: the superuser still logs in.
- [x] **Tooling.** `pyproject.toml` (ruff, basedpyright with `tests/` excluded), `pytest.ini`,
  `.coveragerc` (measures `apps/*/services/*`), one trivial test.
  AC: `ruff check .`, `basedpyright` and `pytest` pass inside the container.
- [ ] **CI.** *(files done and checked outside Docker on 2026-11-03; owner confirms with `commands/Phase_1/day-1.md` step 12)* `.github/workflows/ci.yml` with the `test` job (Postgres service) and a
  `css-fresh` job stub that is completed on Day 2 (`deployment.md` §5).
  AC: green on the first push.
- [x] **Docs in the repo.** Copy this doc set into `docs/` and `CLAUDE.md` into the repo root.
  AC: `docs/errors-and-exceptions/` has its README, `_templates/` and the worked example.

**Done when:** the site answers at `http://localhost:8000` from Postgres, data survives
`down`/`up`, and CI is green.

## Day 2 — Frontend pipeline and base layout

**Goal:** an empty page with the final header and footer on desktop and mobile.

- [x] **npm Sass pipeline.** Root `package.json` with exact versions of `sass`, `bootstrap`,
  `@fortawesome/fontawesome-free`, `@fontsource/open-sans`; scripts `build:css`, `watch:css`,
  `vendor` (`frontend.md` §1); `scripts/copy-vendor.mjs` copies Bootstrap's JS bundle and Open
  Sans `woff2` into `static/vendor/`, and Font Awesome icons as inline SVGs into
  `templates/includes/icons/`.
  AC: `npm run build:css` writes a minified `static/css/main.css` with no `sourceMappingURL`.
- [x] **Brand tokens.** `static/scss/_tokens.scss` (`$dcs-*` and the `--dcs-*` custom
  properties), `_variables.scss` (Bootstrap overrides), `main.scss` import order
  (`frontend.md` §2).
  AC: `$primary` is the brand gold; body text is Open Sans.
- [x] **Base templates.** `base.html`, `includes/_topbar.html`, `_navbar.html` (Home, About Us,
  Services, Contact Us, from a nav list in the context processor), `_footer.html`; skip link;
  placeholder values until `SiteSettings` exists tomorrow.
  AC: the layout matches the old site's structure at 375, 768 and 1280 px.
- [x] **`css-fresh` CI job** completed: `npm ci`, `npm run build:css`, `git diff --exit-code`,
  no source maps.
  AC: a PR with SCSS changed but CSS not rebuilt fails `css-fresh`.
- [x] **WhiteNoise check.** Run the prod `collectstatic` locally (`deployment.md` §2).
  AC: no missing-file errors from vendored fonts.

**Done when:** an empty page renders with the final header and footer, and `css-fresh` is green.

## Day 3 — Core base classes and SiteSettings

**Goal:** the shared building blocks exist, and the header and footer read from the database.

- [ ] **Base classes.** `BaseModel`, `PublishableMixin`, `OrderableMixin`, `SluggedMixin`,
  `BaseRepository[T]`, `BaseService`, `BaseController`, `ServiceError` family
  (`architecture.md` §4).
  AC: unit tests for the generic repository methods (DB) and the controller's error mapping.
- [ ] **SiteSettings singleton.** Phone(s), enquiries email, recruitment email, address, hours,
  footer blurb, social URLs, default meta description, default OG image, GA4 ID, map query.
  Repository, service (defaults when empty), context processor, admin (one row, no delete).
  AC: top bar, footer and social icons render from the DB; an empty URL hides its icon.
- [ ] **Markdown.** `MarkdownService` (`markdown` + `nh3`, allow-list in `architecture.md` §4)
  and the `{% markdown %}` filter.
  AC: the sanitiser tests in `Phase_1/Test_Plan.md` §3.2 pass.
- [ ] **Layering test.** `apps/core/tests/test_layering.py` (`architecture.md` §2).
  AC: adding `from apps.pages.repositories …` to a controller fails the test.
- [ ] **Logging and checks.** `LOGGING` to the console at WARNING; `apps/core/checks.py` with
  `core.W001` (sender not on a real domain), `W002` (Resend without a key), `W003` (SMTP without
  a login) (`deployment.md` §6).
  AC: `check` with prod settings and no `DEFAULT_FROM_EMAIL` prints `core.W001`.

**Done when:** footer and top bar read from the DB, and the layering test guards the rules.

## Day 4 — Users and admin

**Goal:** admins can onboard users who sign in by password or Google; strangers can't sign up.

- [ ] **allauth.** Email login, sign-up closed (both adapters), Google provider, password reset,
  branded `templates/account/` (`users.md` §3).
  AC: `/accounts/signup/` doesn't offer a form; an unknown Google account is refused politely.
- [ ] **UserService.** `onboard_user` (lower-cased email, generated username, unusable password,
  set-password email), `deactivate`; `onboard_user` management command.
  AC: service tests with a fake repository pass.
- [ ] **Groups.** Data migration creating **Content Editor** with the Phase 1 content
  permissions (`users.md` §4).
  AC: a Content Editor can edit pages but not users.
- [ ] **Jazzmin.** Brand title, logo, accent, menu order (`users.md` §5); admin at
  `ADMIN_URL_PATH` (default `admin/` in dev).
  AC: the admin login shows the Distinctive branding.
- [ ] **Google OAuth.** Owner registers redirect URIs for localhost, the preview host and the
  live domain; `GOOGLE_CLIENT_ID`/`SECRET` in `.env`.
  AC: an existing user signs in with Google locally.

**Done when:** an admin creates a user, that user signs in by password or Google, and a stranger
can't sign up.

## Day 5 — Pages app and Home

**Goal:** Home matches the old site's structure, every block editable in the admin.

- [ ] **Models.** `pages.Page` (slug, title, SEO fields), `pages.PageSection` (type, heading,
  Markdown body, image + alt text, layout options, `anchor`, order, published),
  `pages.HeroSlide`; `offerings.Service` (title, `anchor`, summary, Markdown body, image + alt,
  `show_on_home`, order, published).
  AC: migrations apply; `anchor` is unique per page and auto-filled from the heading.
- [ ] **Layers.** `PageRepository`, `PageService.get_page(slug)` (published sections only,
  ordered; `NotFoundError` otherwise), `ServiceRepository`/`OfferingService.home_cards()`,
  `HomeController`.
  AC: service tests with fakes pass.
- [ ] **Templates.** `includes/_section.html` rendering each `section_type`
  (`frontend.md` §3); `pages/home.html`; hero slider (Bootstrap carousel, pause on hover/focus,
  reduced-motion respected).
  AC: hero, six cards, CTA and the two value blocks render from the DB.
- [ ] **Admin.** Page admin with inline sections and slides, ordering, image thumbnails;
  Service admin.
  AC: reordering a section in the admin reorders it on the page.
- [ ] **Seed, part 1.** `seed_site_content` loads Home's real content and the six home services.
  AC: running it twice changes nothing (idempotent).

**Done when:** Home renders from the DB and every block is editable.

## Day 6 — About, team and partners

**Goal:** About renders from the DB with all eight leadership profiles.

- [ ] **Models.** `team.TeamMember` (photo + alt, name, title, Markdown bio, LinkedIn,
  Facebook, order, published); `pages.Partner` (logo + alt, name, caption, URL,
  `kind` = partner | client, order, published).
  AC: migrations apply.
- [ ] **Layers.** `TeamRepository`/`TeamService.leadership()`, `PartnerRepository`/
  `PartnerService.partners()` and `.clients()`, `AboutController`.
  AC: service tests with fakes pass.
- [ ] **About page.** Hero, Our Story (gradient band, two columns), Strategic Partners,
  Capability Analysis, Value Driven and Capacity Building, Our Leadership grid with "Read more"
  collapse for long bios (`frontend.md` §4).
  AC: matches the old structure; bios are left-aligned with a comfortable line length.
- [ ] **Seed, part 2.** About sections, eight team members, partners.
  AC: idempotent.

**Done when:** About renders from the DB with all eight profiles.

## Day 7 — Services page and the contact service

**Goal:** the Services page is complete, and enquiries are saved and emailed (tested, not yet
wired to a page).

- [ ] **Services page.** Static hero with anchor nav, "What We Do", 13 alternating bands (each
  with its `id` anchor), NGO Capacity Development with diagram, corporate-clients logo grid
  (`frontend.md` §4).
  AC: all 13 old-site services exist as `Service` records; anchor links scroll to each.
- [ ] **Contact model and service.** `contact.ContactSubmission` (first/last name or name,
  email, phone optional, message, `source_page`, `email_sent`, `email_error`, `handled`,
  IP hash, user agent); `ContactService.submit` saves first, then emails `CONTACT_RECIPIENT`
  with the submitter as `Reply-To`; failure logged with the provider's message, never raised
  to the visitor (`architecture.md` §5).
  AC: the ContactService tests in `Phase_1/Test_Plan.md` §3.3 pass.
- [ ] **Resend wiring.** `django-anymail[resend]`; `EMAIL_PROVIDER` = `console` | `resend` |
  `smtp` (`deployment.md` §6).
  AC: with `EMAIL_PROVIDER=resend` locally and a real key, a test enquiry arrives in the
  mailbox.
- [ ] **Resend domain (owner).** Verify the sending subdomain in the existing Resend account;
  add its DNS records; create a Sending-access key limited to that domain.
  AC: the domain shows **Verified** in Resend.
- [ ] **Admin.** Submissions read-only, filters (`email_sent`, `handled`, `source_page`),
  actions "Mark as handled" and "Resend notification email".
  AC: an unsent submission can be resent from the admin.

**Done when:** Services is complete, and an enquiry saved through the service reaches the
mailbox.

## Day 8 — Contact page, enquiry block, cookie consent

**Goal:** visitors can send enquiries from Contact and Services; nothing third-party loads before
consent.

- [ ] **Forms and controller.** `ContactForm` (name, email, message) and `EnquiryForm` (first
  name, last name, email, message); honeypot field; rate limit (5 per IP per hour, Django's
  database cache so all gunicorn workers share it); `ContactController` answering HTML or the
  JSON envelope.
  AC: controller tests: valid, invalid, honeypot, rate-limited, non-AJAX fallback.
- [ ] **Contact page.** Black band with the form left and "Reach Us" right (including the
  vacancies line, assumption A3), map band below (`frontend.md` §4).
  AC: the form works with JavaScript off (full-page POST and redirect with a message).
- [ ] **`contact-form.js` and `http.js`.** AJAX submit, field errors, success state, CSRF
  header (`frontend.md` §5).
  AC: errors show next to their fields without a reload.
- [ ] **Services enquiry block.** The gold "Get In Touch With Us" block posts to the same
  controller with `source_page=services`; button "Send enquiry".
  AC: its submissions show "services" in the admin.
- [ ] **Cookie consent.** `_cookie_banner.html`, `cookie-consent.js` (accept / decline, stored
  choice, `consent:granted` event, footer link to reopen) (`frontend.md` §8).
  AC: before a choice, no request goes to Google.
- [ ] **GA4 and the map.** GA4 tag injected only after "Accept"; Maps Embed iframe injected only
  after "Accept", with the address and a "Get directions" link before.
  AC: the Test Plan §4 consent checks pass in the browser's network tab.

**Done when:** an enquiry from either form lands in the admin and the mailbox, and GA and the
map load only after consent.

## Day 9 — SEO, redirects, polish and production files

**Goal:** production-ready: SEO valid, old links redirected, Lighthouse targets met, prod stack
runs locally.

- [ ] **SEO.** `SeoMixin` + `includes/_seo.html` (title, description, canonical, Open Graph,
  Twitter card, JSON-LD `Organization` with address and phone); per-page fields on `Page`.
  AC: each page has a unique title and description.
- [ ] **Sitemap and robots.** `sitemap.xml` (the four pages), `robots.txt` pointing to it and
  disallowing the admin path.
  AC: both validate; the admin path isn't in the sitemap.
- [ ] **Old-URL redirects.** `pages.Redirect` (old path → new path, 301) with an admin and a
  middleware, seeded from the old site's sitemap (for example `/about-us/` → `/about/`, job post
  URLs → `/contact/` until Phase 2).
  AC: every URL in the old sitemap answers 301 to a live page.
- [ ] **Error pages.** Branded `404.html` and `500.html`.
  AC: an unknown URL shows the branded 404 with status 404.
- [ ] **Responsive and accessibility pass.** Every page at 375 / 768 / 1280 px; focus states;
  contrast (darker gold for text on light bands); `alt` texts; `loading="lazy"` except the
  hero; explicit image sizes.
  AC: Lighthouse on Home, About, Services, Contact: Performance ≥ 90, Accessibility ≥ 90,
  SEO ≥ 95.
- [ ] **Seed, part 3.** Services, clients and Contact content; `SiteSettings` values.
  AC: a fresh database plus `seed_site_content` gives the complete site.
- [ ] **Production files.** `docker/docker-compose.prod.yml` (web from GHCR, db with health
  check, caddy; volumes `pg_data`, `media_data`, `caddy_data`), `docker/Caddyfile` (serves
  `/media/*` from the volume, proxies the rest), `.env.prod.example`,
  `.github/workflows/deploy-vps.yml`, `build-and-push` job in CI (`deployment.md` §7).
  AC: the prod stack runs locally at `https://localhost` with `config.settings.prod`; an image
  uploaded in the admin is served by Caddy; `check --deploy` prints no warnings.
- [ ] **Old site backup (owner).** Full WordPress backup (files and database) stored safely.
  AC: the backup file exists off the old host.

**Done when:** Lighthouse targets are met, every old URL redirects, and the prod stack runs
locally.

## Day 10 — VPS, client walkthrough and go-live

**Goal:** the new site is live on `distinctive.co.zw`, signed off by the client.

- [ ] **VPS (owner, with the commands file).** Ubuntu LTS, a non-root deploy user, SSH keys
  only, firewall (22, 80, 443), Docker, the two compose files and `.env` in `/srv/distinctive`
  (`deployment.md` §7).
  AC: `docker compose -f docker-compose.prod.yml config` resolves.
- [ ] **Preview host.** A DNS record such as `new.distinctive.co.zw` → the VPS;
  `SITE_DOMAIN=new.distinctive.co.zw`; first deploy with the `Deploy VPS` workflow; seed the
  content; create the client's users.
  AC: `https://new.distinctive.co.zw` serves the site with a valid certificate; an enquiry
  reaches the mailbox and shows **Email sent: Yes**.
- [ ] **Client walkthrough.** Editing a section, reordering a slide, adding a team member,
  reading and resending an enquiry, Google sign-in (`Phase_1/Test_Plan.md` §4).
  AC: feedback recorded; fixes that fit today are made; the rest go on the Phase 2 board.
- [ ] **Cutover (after sign-off).** Lower the TTL in advance; switch `distinctive.co.zw` and
  `www` to the VPS; set `SITE_DOMAIN` to the live domain (keep `new.` working or redirecting);
  check the redirects, the mail records and the certificate (`deployment.md` §8).
  AC: the live domain serves the new site over HTTPS; email to `enquiries@` still arrives; the
  old sitemap URLs redirect.
- [ ] **Backups.** Nightly `pg_dump` and media archive, copied off the server; one restore
  tested.
  AC: a restore into a scratch database succeeds.
- [ ] **Handover note.** Env checklist, how to add a user, how to deploy and roll back to a
  previous SHA, where enquiries are, backups.
  AC: written in `docs/Operations.md`.
- [ ] **Phase 1 gate.** Work through `Phase_Gates.md` §3; state "Phase 1 build complete." or
  "Phase 1 not complete."

**Done when:** the client has signed off, the live domain serves the new site, and the gate is
affirmed.

---

## Risks and buffers

| Risk | Mitigation |
|---|---|
| Content arrives late | `seed_site_content` loads what the old site already shows; the client edits the rest in the admin after launch |
| DNS access or Resend verification delayed | Console email locally; submissions are always saved (`email_sent=False` visible in the admin); the preview host can run before Resend is verified, the cutover can't |
| The VPS isn't ordered by Day 9 | Production files are proven locally on Day 9; Day 10 only needs SSH and DNS |
| Client feedback on the walkthrough is larger than a day | Cutover waits for sign-off; feedback that isn't a blocker goes to the Phase 2 board |
| Lost mail at cutover | Only web records change; check MX before and after (assumption A1) |
| Day 8 or 9 overruns | Lighthouse tuning and the redirect seed can finish on Day 10 morning before the walkthrough |

## Stretch pool (only if a day finishes early)

- Responsive image sizes (`srcset`) generated on upload.
- An uptime monitor (UptimeRobot free) on the live domain.
- A pre-commit hook running `npm run build:css` when SCSS is staged.
