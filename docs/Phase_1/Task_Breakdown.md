# Phase 1 — Task Breakdown (11 working days)

*Revised 2026-11-04: Day 9, **UI and components polish**, was added after Day 8 at the owner's
request (`Phase_1/Phase1_Scope.md` D16, D17). SEO, redirects and production files moved to Day 10,
and the VPS and go-live to Day 11.*

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
  `@fortawesome/fontawesome-free`, `@fontsource/open-sans` (Nunito Sans since Day 7); scripts `build:css`, `watch:css`,
  `vendor` (`frontend.md` §1); `scripts/copy-vendor.mjs` copies Bootstrap's JS bundle and Open
  Sans `woff2` into `static/vendor/`, and Font Awesome icons as inline SVGs into
  `templates/includes/icons/`.
  AC: `npm run build:css` writes a minified `static/css/main.css` with no `sourceMappingURL`.
- [x] **Brand tokens.** `static/scss/_tokens.scss` (`$dcs-*` and the `--dcs-*` custom
  properties), `_variables.scss` (Bootstrap overrides), `main.scss` import order
  (`frontend.md` §2).
  AC: `$primary` is the brand gold; body text is Open Sans (Nunito Sans since 2026-11-04).
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

- [x] **Base classes.** `BaseModel`, `PublishableMixin`, `OrderableMixin`, `SluggedMixin`,
  `BaseRepository[T]`, `BaseService`, `BaseController`, `ServiceError` family
  (`architecture.md` §4).
  AC: unit tests for the generic repository methods (DB) and the controller's error mapping.
- [x] **SiteSettings singleton.** Phone(s), enquiries email, recruitment email, address, hours,
  footer blurb, social URLs, default meta description, default OG image, GA4 ID, map query.
  Repository, service (defaults when empty), context processor, admin (one row, no delete).
  AC: top bar, footer and social icons render from the DB; an empty URL hides its icon.
- [x] **Markdown.** `MarkdownService` (`markdown` + `nh3`, allow-list in `architecture.md` §4)
  and the `{% markdown %}` filter.
  AC: the sanitiser tests in `Phase_1/Test_Plan.md` §3.2 pass.
- [x] **Layering test.** `apps/core/tests/test_layering.py` (`architecture.md` §2).
  AC: adding `from apps.pages.repositories …` to a controller fails the test.
- [x] **Logging and checks.** `LOGGING` to the console at WARNING; `apps/core/checks.py` with
  `core.W001` (sender not on a real domain), `W002` (Resend without a key), `W003` (SMTP without
  a login) (`deployment.md` §6).
  AC: `check` with prod settings and no `DEFAULT_FROM_EMAIL` prints `core.W001`.
- [x] **Logo** (added 2026-11-03): the client's logo replaces the stand-in.

**Done when:** footer and top bar read from the DB, and the layering test guards the rules.

## Day 4 — Users and admin

**Goal:** admins can onboard users who sign in by password or Google; strangers can't sign up.

- [x] **allauth.** Email login, sign-up closed (both adapters), Google provider, password reset,
  branded `templates/account/` (`users.md` §3).
  AC: `/accounts/signup/` doesn't offer a form; an unknown Google account is refused politely.
- [x] **UserService.** `onboard_user` (lower-cased email, generated username, unusable password,
  set-password email), `deactivate`; `onboard_user` management command.
  AC: service tests with a fake repository pass.
- [x] **Groups.** Data migration creating **Content Editor** with the Phase 1 content
  permissions (`users.md` §4).
  AC: a Content Editor can edit pages but not users.
- [x] **Jazzmin.** Brand title, logo, accent, menu order (`users.md` §5); admin at
  `ADMIN_URL_PATH` (default `admin/` in dev).
  AC: the admin login shows the Distinctive branding.
- [ ] **Google OAuth.** *(code done and tested up to the redirect to Google on 2026-11-03; the owner creates the OAuth client and confirms a real sign-in with `commands/Phase_1/day-4.md` step 9)* Owner registers redirect URIs for localhost, the preview host and the
  live domain; `GOOGLE_CLIENT_ID`/`SECRET` in `.env`.
  AC: an existing user signs in with Google locally.

**Done when:** an admin creates a user, that user signs in by password or Google, and a stranger
can't sign up.

## Day 5 — Pages app and Home

**Goal:** Home matches the old site's structure, every block editable in the admin.

- [x] **Models.** `pages.Page` (slug, title, SEO fields), `pages.PageSection` (type, heading,
  Markdown body, image + alt text, layout options, `anchor`, order, published),
  `pages.HeroSlide`; `offerings.Service` (title, `anchor`, summary, Markdown body, image + alt,
  `show_on_home`, order, published).
  AC: migrations apply; `anchor` is unique per page and auto-filled from the heading.
  *(As built: images through a shared `ImageMixin` that stores width and height and requires alt
  text unless "decorative"; a data migration creates the four pages; a `service_cards` section
  type places Home's cards.)*
- [x] **Layers.** `PageRepository`, `PageService.get_page(slug)` (published sections only,
  ordered; `NotFoundError` otherwise), `ServiceRepository`/`OfferingService.home_cards()`,
  `HomeController`.
  AC: service tests with fakes pass.
- [x] **Templates.** `includes/_section.html` rendering each `section_type`
  (`frontend.md` §3); `pages/home.html`; hero slider (Bootstrap carousel, pause on hover/focus,
  reduced-motion respected).
  AC: hero, six cards, CTA and the two value blocks render from the DB.
  *(As built: plus a pause button and `static/js/main.js` + `modules/hero-slider.js`.)*
- [x] **Admin.** Page admin with inline sections and slides, ordering, image thumbnails;
  Service admin.
  AC: reordering a section in the admin reorders it on the page.
- [x] **Seed, part 1.** `seed_site_content` loads Home's real content and the six home services.
  AC: running it twice changes nothing (idempotent).
  *(As built: it adds only what's missing and never overwrites an editor's change. Images are cut
  from the old site's screenshots until the client sends originals; the hero photo is left out,
  see `frontend.md` §4.)*

**Done when:** Home renders from the DB and every block is editable.

## Day 6 — About, team and partners

**Goal:** About renders from the DB with all eight leadership profiles.

- [x] **Models.** `team.TeamMember` (photo + alt, name, title, Markdown bio, LinkedIn,
  Facebook, order, published); `pages.Partner` (logo + alt, name, caption, URL,
  `kind` = partner | client, order, published).
  AC: migrations apply.
  *(As built: `TeamMember` also has an `anchor`; `PageSection` gained a "short text" (`intro`),
  a heading position, and the section types `partners`, `clients` and `team`.)*
- [x] **Layers.** `TeamRepository`/`TeamService.leadership()`, `PartnerRepository`/
  `PartnerService.partners()` and `.clients()`, `AboutController`.
  AC: service tests with fakes pass.
  *(As built: one `PageController` serves Home and About; `PageBlocksService` fetches the team,
  logos or service cards only for the sections that show them.)*
- [x] **About page.** Hero, Our Story (gradient band, two columns), Strategic Partners,
  Capability Analysis, Value Driven and Capacity Building, Our Leadership grid with "Read more"
  collapse for long bios (`frontend.md` §4).
  AC: matches the old structure; bios are left-aligned with a comfortable line length.
  *(As built: Read more on every screen size, so the cards line up; `static/js/modules/read-more.js`.)*
- [x] **Seed, part 2.** About sections, eight team members, partners.
  AC: idempotent.

**Done when:** About renders from the DB with all eight profiles.

## Day 7 — Services page and the contact service

**Goal:** the Services page is complete, and enquiries are saved and emailed (tested, not yet
wired to a page).

- [x] **Font** (added 2026-11-04, the owner's choice): Nunito Sans replaces Open Sans on the site
  and in the admin (`frontend.md` §1).
- [x] **Services page.** Static hero with anchor nav, "What We Do", 13 alternating bands (each
  with its `id` anchor), NGO Capacity Development with diagram, corporate-clients logo grid
  (`frontend.md` §4).
  AC: all 13 old-site services exist as `Service` records; anchor links scroll to each.
  *(As built: a `service_bands` section type; the seed now also fills empty fields on items an
  earlier day created, which is how Home's six services got their full text.)*
- [x] **Contact model and service.** `contact.ContactSubmission` (first/last name or name,
  email, phone optional, message, `source_page`, `email_sent`, `email_error`, `handled`,
  IP hash, user agent); `ContactService.submit` saves first, then emails `CONTACT_RECIPIENT`
  with the submitter as `Reply-To`; failure logged with the provider's message, never raised
  to the visitor (`architecture.md` §5).
  AC: the ContactService tests in `Phase_1/Test_Plan.md` §3.3 pass.
- [ ] **Resend wiring.** *(code done 2026-11-04 and tested through Django's test backend and a
  failing one; the owner proves a real send with `commands/Phase_1/day-7.md` step 9 once the domain
  is verified)* `django-anymail` and the `EMAIL_PROVIDER` setting (`console` | `resend` |
  `smtp`) were added on Day 3 with the email checks (`config/settings/email.py`); today proves a
  real send (`deployment.md` §6).
  AC: with `EMAIL_PROVIDER=resend` locally and a real key, a test enquiry arrives in the
  mailbox.
- [ ] **Resend domain (owner).** Verify the sending subdomain in the existing Resend account;
  add its DNS records; create a Sending-access key limited to that domain.
  AC: the domain shows **Verified** in Resend.
- [x] **Admin.** Submissions read-only, filters (`email_sent`, `handled`, `source_page`),
  actions "Mark as handled" and "Resend notification email".
  AC: an unsent submission can be resent from the admin.

**Done when:** Services is complete, and an enquiry saved through the service reaches the
mailbox.

## Day 8 — Contact page, enquiry block, cookie consent

**Goal:** visitors can send enquiries from Contact and Services; nothing third-party loads before
consent.

- [x] **Forms and controller.** `ContactForm` (name, email, message) and `EnquiryForm` (first
  name, last name, email, message); honeypot field; rate limit (5 per IP per hour, Django's
  database cache so all gunicorn workers share it); `ContactController` answering HTML or the
  JSON envelope.
  AC: controller tests: valid, invalid, honeypot, rate-limited, non-AJAX fallback.
  *(As built: `RateLimitService` in core counts accepted enquiries only; the visitor's address
  is read behind Caddy through `TRUSTED_PROXY_COUNT`; `createcachetable` is in the entrypoint.)*
- [x] **Contact page.** Black band with the form left and "Reach Us" right (including the
  vacancies line, assumption A3), map band below (`frontend.md` §4).
  AC: the form works with JavaScript off (full-page POST and redirect with a message).
  *(As built: `contact_form` and `map` section types, seeded today rather than in the SEO day's
  seed, part 3.)*
- [x] **`contact-form.js` and `http.js`.** AJAX submit, field errors, success state, CSRF
  header (`frontend.md` §5).
  AC: errors show next to their fields without a reload.
- [x] **Services enquiry block.** The gold "Get In Touch With Us" block posts to the same
  controller with `source_page=services`; button "Send enquiry".
  AC: its submissions show "services" in the admin.
  *(As built: an `enquiry_form` section type, seeded after the client logos.)*
- [x] **Cookie consent.** `_cookie_banner.html`, `cookie-consent.js` (accept / decline, stored
  choice, `consent:granted` event, footer link to reopen) (`frontend.md` §7).
  AC: before a choice, no request goes to Google.
- [x] **GA4 and the map.** GA4 tag injected only after "Accept"; Maps Embed iframe injected only
  after "Accept", with the address and a "Get directions" link before.
  AC: the Test Plan §4 consent checks pass in the browser's network tab.
  *(Checked in a headless browser with a placeholder GA id and key: no Google request before a
  choice, GA4 and the map after Accept, neither after Decline. The real key and GA4 property are
  the owner's; `commands/Phase_1/day-8.md` steps 8–9.)*
- [ ] **Maps key and GA4 property (owner).** Create the Maps Embed API key restricted by HTTP
  referrer to the preview and live hosts, and the GA4 property; put them in `.env` / Site
  settings.
  AC: on the preview host the map shows after Accept, and GA4's Realtime view sees the visit.

**Done when:** an enquiry from either form lands in the admin and the mailbox, and GA and the
map load only after consent.

## Day 9 — UI and components polish

**Goal:** the site looks and feels modern and works in light and dark, without changing what it
says. The old site is a reference for content and structure, not a design to copy
(`Phase_1/Phase1_Scope.md` D17).

- [x] **Light and dark themes.** Theme colours as CSS custom properties (`static/scss/_theme.scss`);
  the system setting (`prefers-color-scheme`) by default; a navbar toggle with **System**,
  **Light** and **Dark**, remembered in `localStorage` and applied before the first paint
  (`static/js/theme-init.js`); a light version of the logo for dark backgrounds
  (`frontend.md` §8).
  AC: with no choice the site follows the system; a chosen theme survives a reload without a
  flash; without JavaScript the system setting still applies and the toggle is hidden.
- [x] **Modern components.** Gradients with soft gold light instead of flat bands; frosted
  service cards that lift on hover; framed images; logo tiles; team cards with gold photo rings;
  rounded buttons and fields; a glass Contact form beside an icon list; the Services enquiry form
  in a card on gold; numbered service bands with chips linking to them; a floating cookie card;
  a three-column footer.
  AC: every page at 375 and 1280 px in both themes reads clearly, with contrast checked (AA).
- [x] **Section labels.** An optional **label** above each section's heading (`PageSection.eyebrow`,
  migration `pages.0008_section_label`), seeded for every section; Contact gains a page hero.
  AC: a label set in the admin shows above its heading.
- [x] **Team bio dialog.** A long bio is cut to a few lines with **Read full bio**, which opens it in a
  native `<dialog>` (`static/js/modules/bio-dialog.js`, replacing `read-more.js`).
  AC: Escape closes it and focus returns to the button; without JavaScript the whole bio shows.
- [x] **Motion.** Sections and cards fade up as they scroll into view (`reveal.js`); hover lifts and
  arrow nudges; the hero's gold light drifts; the navbar gains a shadow on scroll (`navbar.js`).
  All of it is off with reduced motion, and nothing is hidden unless the script has started.
  AC: with reduced motion every card is visible at once; without JavaScript nothing is hidden.
- [x] **Back to top.** A round gold button bottom right (`back-to-top.js`): a plain link to `#top`
  without JavaScript; with it, it appears after scrolling, scrolls up smoothly and moves focus to
  the logo.
  AC: it appears after scrolling, returns to the top and works by keyboard.
- [x] **Hero backgrounds** (added 2026-11-04, the owner's choice): Home's hero shows the team
  photo the owner sent (`seed/images/team-photo.jpg`, 1600 px, about 280 KB), with the text over
  the trees and the team's faces clear at every width; the page heroes on About, Services and
  Contact, and the Contact form's band, use the drifting black-and-gold gradient (it had been
  hidden behind plain black by a CSS ordering slip, now fixed).
  AC: on Home the heading and tagline never cover a face at 375, 768, 1280 or 1920 px.
  *(Revised 2026-11-04 evening: the photo's darkening overlay no longer sits over the photo-less
  heroes, so their gradient shows at full strength; Home's photo hero is shorter on phones, so
  the crop keeps more of the team and less lawn.)*
- [x] **No sideways scroll on phones** (found 2026-11-04 while taking the stakeholder screenshots):
  rows with Bootstrap's `g-5` gutter were 12 px wider than a phone screen, so every page scrolled
  sideways. They now use `g-4` below 992 px (`g-4 g-lg-5`).
  AC: at 390 px nothing on any page is wider than the screen (checked in the browser on all
  four pages).

**Done when:** all four pages are polished in both themes, the checks pass, and nothing that
worked on Day 8 (forms, consent, the slider) has changed behaviour.

## Day 10 — SEO, redirects, polish and production files

**Goal:** production-ready: SEO valid, old links redirected, Lighthouse targets met, prod stack
runs locally.

*(Started on 2026-11-04 before the polish day was added; the code shipped in the Day 9 zip, and
was checked, finished and documented on 2026-11-05. The owner also moved the **demo** forward to
this day, the stakeholder email of 2026-11-04 having promised one on Thursday 5 November: the
preview host goes up today, and Day 11 keeps the walkthroughs and the cutover.)*

- [x] **SEO.** `SeoMixin` + `includes/_seo.html` (title, description, canonical, Open Graph,
  Twitter card, JSON-LD `Organization` with address and phone); per-page fields on `Page`.
  AC: each page has a unique title and description.
  *(As built: `SeoService` (`apps/core/services/seo_service.py`) rather than a mixin, called by
  `PageController`; canonical and Open Graph addresses come from `SITE_URL`, never the request's
  host; the `Organization` JSON-LD is on Home only; `SEO_NOINDEX=true` (the preview host) adds
  `noindex, nofollow` everywhere. Sign-in and error pages get a plain title and `noindex`.)*
- [x] **Sitemap and robots.** `sitemap.xml` (the four pages), `robots.txt` pointing to it and
  disallowing the admin path.
  AC: both validate; the admin path isn't in the sitemap.
  *(As built: `robots.txt` does not name the admin, since that would publish its unguessable
  address; it disallows `/accounts/`, and on the preview host everything.)*
- [x] **Old-URL redirects.** `pages.Redirect` (old path → new path, 301) with an admin and a
  middleware, seeded from the old site's sitemap (for example `/about-us/` → `/about/`, job post
  URLs → `/contact/` until Phase 2).
  AC: every URL in the old sitemap answers 301 to a live page.
  *(As built: nine seeded redirects from the addresses the screenshots and WordPress's defaults
  show, with "and everything under it" prefixes for categories and jobs; job addresses are 302
  to Contact, so they can change when Phase 2 adds Jobs. Only requests that would be a 404 are
  redirected, so a redirect never hides a live page; hits are counted in the admin.
  `manage.py check_redirects <sitemap>` checks the old sitemap once the owner exports it.)*
- [ ] **Old sitemap (owner).** Export the old site's `wp-sitemap.xml` (and the sitemaps it lists)
  and run `check_redirects` on them (`commands/Phase_1/day-10.md` step 8).
  AC: every address prints OK; anything MISSING gets a redirect in the admin.
- [x] **Error pages.** Branded `404.html` and `500.html`.
  AC: an unknown URL shows the branded 404 with status 404.
  *(As built: `500.html` uses no context processor or database, so it shows even when those
  are what failed.)*
- [x] **Responsive and accessibility pass.** Every page at 375 / 768 / 1280 px; focus states;
  contrast (darker gold for text on light bands); `alt` texts; `loading="lazy"` except the
  hero; explicit image sizes.
  AC: Lighthouse on Home, About, Services, Contact: Performance ≥ 90, Accessibility ≥ 90,
  SEO ≥ 95.
  *(Measured 2026-11-05 on prod settings under gunicorn, with uploads served as Caddy will:
  mobile Performance 94–98, Accessibility 100, Best Practices 100, SEO 100 on all four pages;
  desktop 100 throughout. Home first measured 87 on mobile once the team photo actually loaded,
  hence the next card.)*
- [x] **Responsive images** (promoted from the stretch pool on 2026-11-05). `ImageVariantService`
  makes WebP copies of each upload at 480, 800, 1200, 1600 and 2000 px (never wider than the
  original) the first time a page needs them, under `media/variants/`; `_image.html` gives every
  image a `srcset`, and a `sizes` hint where the layout is known.
  AC: a phone fetches the team photo as a WebP of about 90 KB instead of the 280 KB JPEG; Home's
  mobile Performance is 90 or more (94, with LCP 3.0 s instead of 3.9 s).
- [x] **Seed, part 3.** Services, clients and Contact content *(all three seeded by Day 8)*;
  `SiteSettings` values.
  AC: a fresh database plus `seed_site_content` gives the complete site.
  *(`SiteSettings` gets the old site's details from its data migration; the seed adds the
  redirects.)*
- [ ] **Production files.** `docker/docker-compose.prod.yml` (web from GHCR, db with health
  check, caddy; volumes `pg_data`, `media_data`, `caddy_data`), `docker/Caddyfile` (serves
  `/media/*` from the volume, proxies the rest), `.env.prod.example`,
  `.github/workflows/deploy-vps.yml`, `build-and-push` job in CI (`deployment.md` §7).
  AC: the prod stack runs locally at `https://localhost` with `config.settings.prod`; an image
  uploaded in the admin is served by Caddy; `check --deploy` prints no warnings.
  *(Files done and reviewed 2026-11-05. Checked here without Docker, since Docker Hub isn't
  reachable from the build workspace: `collectstatic` with the manifest storage, `check --deploy`
  clean, gunicorn with prod settings serving all four pages, robots, the sitemap, a 301 and the
  404, with the security headers. The owner confirms the whole stack with
  `commands/Phase_1/day-10.md` step 10 or, directly, on the VPS in step 11.)*
- [ ] **Demo on the preview host (owner, moved here from Day 11 on 2026-11-05).** The VPS set up
  (`deployment.md` §7), `new.distinctive.co.zw` pointed at it, GitHub's `production` secrets,
  the first **Deploy VPS** run with `SEED_SITE_CONTENT=true` and `SEO_NOINDEX=true`
  (`commands/Phase_1/day-10.md` step 11).
  AC: `https://new.distinctive.co.zw` shows the site with a valid certificate, and is
  `noindex`; an enquiry is saved (and emailed once Resend is verified).
- [ ] **Old site backup (owner).** Full WordPress backup (files and database) stored safely.
  AC: the backup file exists off the old host.

**Done when:** Lighthouse targets are met, every old URL redirects, and the prod stack runs
locally.

## Day 11 — VPS, client walkthrough and go-live

**Goal:** the new site is live on `distinctive.co.zw`, signed off by the client.

- [ ] **VPS (owner, with the commands file).** Ubuntu LTS, a non-root deploy user, SSH keys
  only, firewall (22, 80, 443), Docker, the two compose files and `.env` in `/srv/distinctive`
  (`deployment.md` §7).
  AC: `docker compose -f docker-compose.prod.yml config` resolves.
- [ ] **Preview host.** *(Set up on Day 10 for the demo; today, finish it.)* A DNS record such as
  `new.distinctive.co.zw` → the VPS; `SITE_DOMAIN=new.distinctive.co.zw`; first deploy with the
  `Deploy VPS` workflow; seed the content; create the client's users.
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
| The VPS isn't ordered by Day 10 | Production files are proven locally on Day 10; Day 11 only needs SSH and DNS |
| Client feedback on the walkthrough is larger than a day | Cutover waits for sign-off; feedback that isn't a blocker goes to the Phase 2 board |
| Lost mail at cutover | Only web records change; check MX before and after (assumption A1) |
| Day 9 or 10 overruns | Lighthouse tuning and the redirect seed can finish on Day 11 morning before the walkthrough |

## Stretch pool (only if a day finishes early)

- ~~Responsive image sizes (`srcset`) generated on upload.~~ Done on Day 10, made on first use.
- An uptime monitor (UptimeRobot free) on the live domain.
- A pre-commit hook running `npm run build:css` when SCSS is staged.
