# Folder Structure

**Project-wide · revised 2026-11-04** (Day 7: Services page, enquiries, Nunito Sans; Day 6: team,
partners, page blocks; Day 5: seed content,
Home templates, JS; 2026-11-02: npm
and SCSS at the repo root, as in Consult 360; Phase 2 apps marked; no R2)

## 1. Repository layout

```
distinctive-site/
├── .github/
│   └── workflows/
│       ├── ci.yml                      # test, css-fresh, build-and-push (main only)
│       └── deploy-vps.yml              # manual: SSH to the VPS, compose pull + up -d
├── apps/
│   ├── core/                           # base classes, SiteSettings, SEO, Markdown, checks, redirects middleware
│   ├── users/                          # User + manager, allauth adapters, UserService, onboard_user, permissions
│   ├── pages/                          # Page, PageSection, HeroSlide, Partner, Redirect
│   ├── offerings/                      # Service (the consulting services)
│   ├── team/                           # TeamMember
│   ├── contact/                        # ContactSubmission, contact + enquiry forms, email
│   ├── jobs/                           # Phase 2: JobPosting
│   └── search/                         # Phase 2: SearchEntry, indexer, search controllers
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── email.py                    # EMAIL_PROVIDER → backend and email settings
│   │   ├── dev.py
│   │   ├── test.py
│   │   └── prod.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── docker/
│   ├── Dockerfile                      # one file, two variants (REQUIREMENTS build arg)
│   ├── entrypoint.sh                   # fingerprint check, wait for db, migrate, exec
│   ├── docker-compose.yml              # local dev: web + db; volumes pg_data, media_data
│   ├── docker-compose.prod.yml         # VPS: web (GHCR) + db + caddy; volumes pg_data, media_data, caddy_data
│   └── Caddyfile                       # HTTPS, /media/ from the volume, proxy to web
├── docs/                               # this doc set (index: docs/README.md)
├── scripts/
│   └── copy-vendor.mjs                 # Bootstrap JS + Nunito Sans → static/vendor/; Font Awesome SVGs → templates/includes/icons/
├── static/
│   ├── scss/                           # SOURCE, compiled on the dev machine (not in the image)
│   │   ├── main.scss                   # entry: tokens → variables → bootstrap → partials
│   │   ├── admin.scss                  # the Jazzmin admin's few rules → static/css/admin.css
│   │   ├── _tokens.scss                # $dcs-* brand tokens and --dcs-* custom properties
│   │   ├── _variables.scss             # Bootstrap variable overrides
│   │   ├── _fonts.scss
│   │   ├── _base.scss
│   │   ├── components/
│   │   │   ├── _topbar.scss
│   │   │   ├── _navbar.scss
│   │   │   ├── _hero.scss
│   │   │   ├── _section.scss           # alternating dark/light bands
│   │   │   ├── _cards.scss             # service card, team card
│   │   │   ├── _forms.scss
│   │   │   ├── _footer.scss
│   │   │   ├── _auth.scss              # sign-in and the other allauth pages
│   │   │   ├── _buttons.scss           # the outlined gold buttons
│   │   │   ├── _logos.scss             # partner and client logo grids
│   │   │   ├── _team.scss              # Our Leadership, Read more
│   │   │   ├── _services.scss          # the Services page links and bands
│   │   │   └── _cookie-banner.scss
│   │   └── pages/
│   │       ├── _home.scss
│   │       ├── _about.scss
│   │       ├── _services.scss
│   │       └── _contact.scss           # Phase 2 adds _jobs.scss and components/_search.scss
│   ├── css/
│   │   ├── main.css                    # COMPILED, minified, committed
│   │   └── admin.css                   # COMPILED from admin.scss, committed
│   ├── js/
│   │   ├── main.js                     # entry (ES module)
│   │   └── modules/
│   │       ├── hero-slider.js          # Home carousel: reduced motion, pause on focus, pause button
│   │       ├── read-more.js            # long bios cut behind Read more
│   │       ├── http.js                 # fetch wrapper: CSRF, JSON envelope, timeout
│   │       ├── contact-form.js
│   │       └── cookie-consent.js       # Phase 2 adds search-dropdown.js, highlight.js
│   ├── vendor/                         # copied from node_modules by `npm run vendor`, committed
│   │   ├── bootstrap/                  # bootstrap.bundle.min.js (source-map line removed)
│   │   └── nunito-sans/                # latin woff2, 400/600/700, normal and italic
│   └── img/                            # logo.png (the client's logo, 172 × 100), later favicons and defaults
├── templates/
│   ├── base.html
│   ├── includes/
│   │   ├── _seo.html
│   │   ├── _topbar.html
│   │   ├── _navbar.html
│   │   ├── _footer.html
│   │   ├── _cookie_banner.html
│   │   ├── icons/                      # inline SVG icons, written by `npm run vendor`
│   │   ├── _hero_slider.html           # Home's slides (pages.HeroSlide)
│   │   ├── _section.html               # renders one PageSection by type
│   │   ├── _service_card.html          # one offerings.Service card
│   │   ├── _logo_grid.html             # pages.Partner logos
│   │   ├── _service_bands.html         # every service as a band, with links
│   │   ├── _team_card.html             # one team.TeamMember
│   │   └── _image.html                 # an admin image with its stored size and alt text
│   ├── errors/
│   │   ├── 404.html
│   │   └── 500.html
│   ├── allauth/layouts/                # base.html wraps every allauth page in the site's layout
│   └── account/                        # our sign-in and set-password pages
├── media/                              # local uploads in dev (git-ignored); a Docker volume in prod
├── requirements/
│   ├── base.txt
│   ├── prod.txt                        # -r base.txt
│   └── dev.txt                         # -r prod.txt
├── .coveragerc                         # measures apps/*/services/*
├── .dockerignore
├── .editorconfig
├── .env.example
├── .env.prod.example
├── .gitignore
├── CLAUDE.md
├── manage.py
├── package.json                        # dev-machine and CI only
├── package-lock.json
├── pyproject.toml                      # ruff, basedpyright (tests excluded)
├── pytest.ini
└── README.md
```

## 2. Inside one app

Every app has the same shape. Example: `apps/contact/`

```
apps/contact/
├── __init__.py
├── apps.py
├── models.py                       # ContactSubmission(BaseModel)
├── admin.py                        # read-only fields, filters, actions (direct ORM: documented exception)
├── forms.py                        # ContactForm, EnquiryForm (honeypot)
├── urls.py
├── repositories/
│   ├── __init__.py
│   └── contact_repository.py       # ContactRepository(BaseRepository)
├── services/
│   ├── __init__.py
│   └── contact_service.py          # ContactService(BaseService)
├── controllers/
│   ├── __init__.py
│   └── contact_controller.py       # ContactController(BaseController)
├── templates/
│   └── contact/
│       ├── contact.html
│       └── _enquiry_form.html      # included on the Services page
├── migrations/
└── tests/
    ├── test_contact_service.py     # fake repository + fake mailer, no DB: the gate
    ├── test_contact_repository.py  # a few DB tests
    └── test_contact_controller.py  # smoke + form behaviour
```

## 3. `apps/core/` in detail

```
apps/core/
├── models.py                  # BaseModel, PublishableMixin, OrderableMixin, SluggedMixin, ImageMixin, SiteSettings
├── admin_widgets.py           # image_preview(): thumbnails in the content admins
├── repositories/
│   ├── base.py                # BaseRepository[T]
│   └── site_settings_repository.py
├── services/
│   ├── base.py                # BaseService
│   ├── markdown_service.py    # Markdown → sanitised HTML
│   ├── navigation_service.py  # the nav items, with the current page marked
│   ├── seed_service.py        # SeedService: adds the old site's content that's missing
│   ├── site_details.py        # SiteDetails value + DEFAULTS (the old site's details)
│   └── site_settings_service.py
├── controllers/
│   └── base.py                # BaseController (View) + error mapping
├── exceptions.py              # ServiceError, NotFoundError, ValidationError, ExternalServiceError
├── checks.py                  # core.W001–W003 (email configuration)
├── context_processors.py      # site_info (SiteDetails), nav_items, current_year
├── middleware.py              # RedirectMiddleware (old WordPress URLs → 301)
├── seo.py                     # SeoMixin, SeoData, sitemaps
├── templatetags/
│   └── core_extras.py         # the |markdown filter
├── seed/
│   ├── content.py             # the old site's text, keyed (anchors, headings)
│   └── images/                # 30 images cut from the old site's screenshots, until the originals come
├── management/commands/
│   └── seed_site_content.py   # loads seed/ through SeedService (idempotent)
└── tests/
    ├── test_layering.py
    ├── test_markdown_service.py
    ├── test_checks.py
    ├── test_seed.py           # SeedService with fakes; the command twice on a real database
    └── test_security.py       # check --deploy with prod settings
```

`apps/pages/` as built by Day 6: `models.py` (`Page`, `PageSection`, `Partner`, `HeroSlide`),
`admin.py` (each page with its slides and sections inline; partners and clients),
`repositories/` (`page_repository.py`, `partner_repository.py`), `services/`
(`page_service.py` with `PageService` and `PageContent`, `partner_service.py`,
`page_blocks_service.py`), `controllers/page_controller.py` (`PageController`, `HomeController`,
`AboutController`, `ServicesController`), `urls.py`, `templates/pages/` (`page.html`, `home.html`), and migrations
`0001_initial`, `0002_the_four_pages`, `0003_partner_section_layout`, `0004_service_bands`.
`apps/offerings/` has `Service`, its admin, `ServiceRepository` and `OfferingService`.
`apps/contact/` (Day 7) has `ContactSubmission`, its admin, `ContactRepository`,
`ContactService` and tests; its forms, controller and templates (§2) arrive on Day 8. `apps/team/` has `TeamMember`,
its admin, `TeamRepository` and `TeamService`.

`Redirect` is a model in `apps/pages` (editable in the admin); the middleware in `apps/core`
reads it through `RedirectService`.

## 4. Naming conventions

| Thing | Convention | Example |
|---|---|---|
| Repository | `<Thing>Repository` in `<thing>_repository.py` | `PageRepository` |
| Service | `<Thing>Service` in `<thing>_service.py` | `ContactService` |
| Controller | `<Thing>Controller` or `<Action><Thing>Controller`, one per file | `AboutController` |
| URL names | `<app>:<action>` | `pages:about` |
| Templates | `<app>/<action>.html`; partials prefixed `_` | `contact/_enquiry_form.html` |
| SCSS partials | prefixed `_`, one per component or page | `_cards.scss` |
| JS modules | kebab-case, one responsibility each | `cookie-consent.js` |
| Error log folders | `<error-slug>__<YYYY-MM-DD_HHMM>` | `resend-refuses-unverified-sender__2026-11-10_1430` |
| Commands files | `docs/commands/Phase_N/day-M.md` | `commands/Phase_1/day-3.md` |

## 5. Dependency direction (never reversed)

```
Controller → Service → Repository → Model
                ↘ other services (allowed; keep it shallow)
```

`apps/core/tests/test_layering.py` fails CI if a controller imports a repository or
`django.db.models`, or if a service file contains `.objects`.

## 6. Git hygiene

- **Committed:** `static/css/main.css` (compiled, minified), `static/vendor/**`, `static/js/**`,
  `package-lock.json`.
- **Ignored:** `node_modules/`, `media/`, `.env`, `.env.prod`, `*.css.map`, `staticfiles/`,
  `__pycache__/`, `.coverage`.
- **`.dockerignore`:** `.git`, `node_modules/`, `package*.json`, `static/scss/`, `scripts/`,
  `docs/`, `media/`, `.env*`.
