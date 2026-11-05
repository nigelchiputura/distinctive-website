> **Superseded 2026-11-02.** Replaced by `Phase_1/Task_Breakdown.md` and `Phase_2/Task_Breakdown.md`
> (two phases; Resend instead of Brevo; local media instead of R2; VPS go-live instead of a Render
> demo). Kept as the record of the original plan.

# Task Breakdown — 15 Working Days (3 weeks × 5 days)

Distinctive Consultancy Services website redesign. Django SSR + Postgres + Docker, five-layer
architecture (`architecture.md`), Bootstrap + SCSS (Dart Sass via npm on the dev machine), pipeline
per `deployment.md`.

**Conventions for every day:** work in a branch, open a PR, CI must be green before merge; log any
non-trivial error under `docs/errors-and-exceptions/` (see `Errors_And_Exceptions.md`); each day ends
with something demonstrable.

## Scope recap

| Item | Decision |
|---|---|
| Pages | Home, About, Services, Jobs (list + detail), Contact, Search results |
| Content | Page sections, hero slides, services, team, partners/clients, jobs, site settings — all admin-editable |
| Jobs | Markdown description, closing date, department, location, employment type; apply by email and/or link only |
| Contact | Saved to DB + emailed to enquiries@distinctive.co.zw |
| Search | Navbar dropdown (AJAX) + results page; Postgres FTS over a unified index; highlight on arrival |
| Auth | `AbstractUser`, no public sign-up, admin-onboarded, Google login via allauth, Jazzmin admin |
| Extras | SEO (meta, OG, sitemap, robots), cookie banner, analytics after consent |
| Deploy | Render demo; VPS compose config built and tested locally |

---

## WEEK 1 — Foundation, content system, Home and About

### Day 1 — Environment and project skeleton
- Create repo, `.gitignore`, `.env.example`, `README.md`.
- Django project (`config/settings/{base,dev,prod,test}.py`), apps scaffolded with the layer folders.
- `docker/Dockerfile`, `docker-compose.yml` with a `pg_data` volume; `entrypoint.sh`.
- Postgres connected; `migrate` runs; admin reachable.
- `ruff` + `pytest-django` configured; first trivial test passing.
- GitHub Actions `ci.yml` (lint + test) green on first push.
- Create `docs/` with the seven docs and the `errors-and-exceptions/` skeleton + example entry.
- Create the Cloudflare R2 bucket(s) and API token; wire `django-storages` behind a `USE_R2` flag (local files in dev).
- **Done when:** `docker compose up` serves a Django page backed by Postgres; data survives `docker compose down` / `up`.

### Day 2 — Frontend pipeline and base layout
- `frontend/` with `package.json`; Dart Sass (`sass`) + Bootstrap 5 installed; `npm run build` / `watch`.
- `_variables.scss` with brand tokens (black / gold / white, Open Sans); `main.scss` ordering (variables → Bootstrap → partials).
- Compiled `static/css/main.css` committed; copy `bootstrap.bundle.min.js` to `static/js/vendor/`.
- `base.html`, top bar (phone, email, and social icons from SiteSettings — only the ones with a URL filled in), navbar (Home, About Us, Services, Jobs, Contact Us, search icon), footer ("Reach Us", footer nav, copyright).
- CI step: SCSS freshness check.
- **Done when:** an empty page renders with the final header/footer on desktop and mobile.

### Day 3 — Core base classes and SiteSettings
- `apps/core`: `BaseModel`, mixins, `BaseRepository`, `BaseService`, `BaseController`, exceptions.
- `SiteSettings` singleton (phone, email, address, hours, social links, default meta, analytics ID) + repository/service + context processor; wired into topbar and footer.
- Markdown service (`markdown` + `nh3`) and `{% markdown %}` filter.
- `core/tests/test_layering.py` import-rule test; base class unit tests.
- **Done when:** footer and topbar read from the DB; layering test enforces the rules.

### Day 4 — Users module and admin
- Custom `User(AbstractUser)` created **before the first migration of anything else** (swap `AUTH_USER_MODEL`).
- allauth: email login, signup closed, Google provider, branded login template.
- Jazzmin theme configured with brand colours/logo; "Content Editor" group seeded.
- `UserService`/`UserRepository` for onboarding helpers; tests for adapters (signup closed, Google login only for existing users).
- **Done when:** an admin can create a user, that user can log in by password or Google, and strangers cannot sign up.

### Day 5 — Pages app and Home page
- Models: `Page`, `PageSection` (type + Markdown body + image + order), `HeroSlide`.
- Repositories/services/controllers; `_section.html` renders each section type.
- Home: hero slider (3 slides), six service cards, "Get In Touch" CTA, two alternating value blocks (People Centred / Proactive).
- Admin: inline sections and slides on the Page.
- **Done when:** Home matches the old site's structure and every block is editable from admin.

---

## WEEK 2 — Services, Team, Jobs, Contact, Search

### Day 6 — About page, team and partners
- `team.TeamMember` (photo, name, title, bio Markdown, LinkedIn/Facebook, order); `pages.Partner` (logo, name, kind = partner | client).
- About: hero, Our Story (two columns), Strategic Partners, Capability Analysis, Value Driven and Capacity Building, Our Leadership grid.
- **Done when:** About renders from DB with all eight leadership profiles.

### Day 7 — Services page
- `offerings.Service` (title, summary, Markdown body, image, order, `show_on_home`).
- Services page: intro ("What We Do"), alternating dark/light service bands, NGO Capacity Development with image, corporate-clients logo grid, enquiry form block.
- Home service cards sourced from `show_on_home` services.
- **Done when:** all thirteen old-site service sections exist as editable `Service` records.

### Day 8 — Jobs
- `jobs.JobPosting`: title, slug, department, location, employment type, closing date, Markdown description, `apply_email`, `apply_url`, optional image, published flag.
- `JobService`: open jobs only (published and closing date not passed), pagination, detail; closed jobs 404 (or show "closed" state — decided Day 8).
- List cards + detail page ("How to apply" block built from `apply_email`/`apply_url`); sidebar with recent postings.
- Admin Markdown editor (EasyMDE, vendored) on the description field.
- **Done when:** an admin can publish a job in Markdown and it renders as sanitized HTML with a working apply link.

### Day 9 — Contact form and email
- `contact.ContactSubmission`; `ContactForm` (name, email, message) with honeypot + basic rate limit.
- `ContactService.submit`: save first, then email `CONTACT_RECIPIENT` through `django-anymail` (Brevo HTTP API); `Reply-To` is the submitter; `email_sent` flag; failure logged, never lost.
- Verify the sending domain (SPF/DKIM/DMARC DNS records on distinctive.co.zw); send a test from the demo.
- AJAX submission (`contact-form.js`) with progressive fallback to normal POST; success/error states.
- Contact page: form, "Reach Us" panel from SiteSettings, interactive Google Map (Maps Embed API iframe, loaded only after cookie consent, with a static address/directions fallback).
- Services-page "Get In Touch" block becomes a general enquiry form (first name, last name, email, message) reusing the same service; submissions are tagged with their source page.
- **Done when:** a submission lands in the DB and in the inbox; admin can see/mark submissions.

### Day 10 — Search backend
- `search.SearchEntry` with GIN-indexed `search_vector`; `SearchRepository`, `SearchIndexService`, `SearchService`.
- `to_search_entry()` on `PageSection`, `Service`, `TeamMember`, `JobPosting`; signals call `SearchIndexService`.
- `rebuild_search_index` command; entrypoint hook.
- Endpoints: `GET /search/suggest/?q=` (JSON, prefix) and `GET /search/?q=` (results page, ranked, snippets, paginated).
- **Done when:** the service-layer search suite (see `testing.md` §5) passes.

### Day 11 — Search frontend and highlighting
- Navbar search input + dropdown (`search-dropdown.js`): debounce, keyboard navigation, ARIA combobox, Enter → results page.
- Results page template with type badges.
- `highlight.js`: reads `?q=`, wraps matches in `<mark>`, scrolls to first, next/prev controls, skips scripts/inputs.
- **Done when:** typing finds content across all pages and clicking a result lands on the page with matches highlighted.

---

## WEEK 3 — Polish, SEO, tests, deployment, handover

### Day 12 — SEO, cookie banner, analytics
- `SeoMixin` + `_seo.html`: title, description, canonical, Open Graph/Twitter, JSON-LD `Organization` and `JobPosting`.
- `sitemap.xml` (static pages + services + open jobs), `robots.txt`.
- Cookie banner (accept / decline, stored choice); GA4 loaded **only after consent**; consent also gates any map embed.
- **Done when:** sitemap/robots validate and GA does not fire before consent.

### Day 13 — Responsive polish, accessibility, error pages
- Pass over every page at mobile / tablet / desktop; image `loading="lazy"` and sizes; focus states, contrast, skip link, ARIA on search and slider.
- Custom 404/500; Lighthouse pass (target: Performance and Accessibility ≥ 90, SEO ≥ 95).
- Slider/animation behaviour respects `prefers-reduced-motion`.
- **Done when:** Lighthouse targets met on Home, Services and Jobs.

### Day 14 — Tests complete, CI/CD, demo deployment
- Fill test gaps per `testing.md` (service layer, search suite, controller smoke, sanitiser/XSS, sitemap).
- Finish CI: coverage thresholds, image build and push to GHCR (`:sha`, `:latest`).
- Render: web service + managed Postgres + env vars; storage option for media decided; `SEED_DEMO_DATA=true`.
- Build and locally verify `docker-compose.prod.yml` + Caddyfile.
- **Done when:** a push to `main` runs CI, publishes the image and deploys the demo URL.

### Day 15 — Content, UAT and handover
- `seed_demo_data` finalised with the real old-site content (team bios, services, partners, clients, jobs).
- Client walkthrough of admin: editing a section, adding a job, reading contact submissions, adding a team member.
- Fix review feedback; final error-log index review.
- Handover notes: env var checklist, Google OAuth redirect URIs, SMTP, backups, how to add a user, how to roll back to a previous SHA.
- Backlog of deferred items recorded.
- **Done when:** client signs off the demo and the production cutover checklist is ready.

---

## Risks and buffers

| Risk | Mitigation |
|---|---|
| Search takes longer than two days | Dropdown can ship on prefix match alone; ranking/snippets can follow |
| Email domain not yet verified / DNS access delayed | Console backend in dev; `email_sent=false` submissions visible in admin; need someone with DNS access for distinctive.co.zw by Day 9 |
| R2 setup (account, payment method, public URL) | Done Day 1; demo uses the r2.dev URL, production needs a custom domain on Cloudflare DNS or an alternative |
| Old-site content volume | Day 15 seed command + client pastes remaining content into admin |
| Google OAuth redirect URIs per env | Register localhost, demo, production URIs on Day 4 |
| Maps API key | Create a Maps Embed key with referrer restrictions before Day 9 |

## Deferred (conscious backlog)

- Multi-language, blog/news, job applications on-site, 2FA, CDN/object storage, zero-downtime deploys.
