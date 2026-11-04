# Phase 1 — Test Plan

**Status:** Agreed 2026-11-02

The required automated tests and the manual QA checklist for Phase 1. The approach, tooling and
CI gate are in `Testing_Strategy.md`. Sections are numbered 3 and 4 so references like "§3.3"
match the Consult 360 layout.

## 3. Required test cases

### 3.1 Core (`apps/core`)

- [x] `BaseRepository`: `get`, `get_or_none`, `list`, `create`, `update`, `delete`, `exists`,
  `count`, and `published()` on a publishable model (DB).
- [x] `OrderableMixin` default ordering; `SluggedMixin` generates unique slugs (`about`,
  `about-2`).
- [x] `BaseController` maps `NotFoundError` → 404, `ValidationError` → 400 (JSON) or the form
  re-rendered (HTML), `ExternalServiceError` → 503 JSON / friendly page; the JSON envelope shape
  is `{ok, data}` / `{ok, errors}`.
- [x] `SiteSettingsService`: returns defaults when no row exists; only one row can exist; social
  links with empty URLs are left out.
- [x] Layering test: a controller importing a repository or the ORM fails; a service using
  `.objects` fails.
- [x] Checks: `core.W001` for a `localhost`/`example.*`/empty sender; `W002` for Resend without
  a key; `W003` for SMTP without a login; none with a correct configuration.

### 3.2 Markdown sanitiser (`MarkdownService`, mandatory)

Admin Markdown is rendered publicly, so these are as important as any business rule.

- [x] `<script>`, inline event handlers (`onerror=`, `onclick=`), `javascript:` and `data:`
  links, `<iframe>`, `<style>` and `<form>` are stripped.
- [x] Headings, paragraphs, lists, bold, italic, blockquotes and links survive; external links
  get `rel="noopener noreferrer"`; `mailto:` and `tel:` links survive.
- [x] Raw HTML in the Markdown source is escaped or stripped, never rendered as written.
- [x] Empty or `None` input returns an empty string.

### 3.3 Contact (`ContactService`, `ContactController`)

Service (fake repository and fake mailer):

- [x] The submission is saved **before** the email is attempted.
- [x] A successful send sets `email_sent=True`.
- [x] A failed send leaves `email_sent=False`, records the provider's message in `email_error`,
  logs a warning, and does **not** raise to the caller.
- [x] The recipient comes from `CONTACT_RECIPIENT`; `Reply-To` is the submitter; the subject
  names the source page.
- [x] HTML in the message is sent as plain text, never as HTML.
- [x] `resend(submission)` (the admin action) sends again and updates the flags.

Controller:

- [x] Valid AJAX POST → 200 `{ok: true}`; invalid → 400 with field errors.
- [x] Valid non-AJAX POST → redirect with a success message; invalid → the page re-rendered with
  errors.
- [x] Honeypot filled → treated as success to the bot, **nothing saved**.
- [x] Sixth submission from one IP within the hour → 429 (JSON) or a friendly message (HTML).
- [x] The Services enquiry form stores `source_page=services`.
- [x] POST without a CSRF token → 403.

### 3.4 Content services

- [x] `PageService.get_page`: unpublished sections excluded; ordered by `sort_order`; a missing
  or unpublished page raises `NotFoundError`.
- [x] `PageSection.anchor` is generated from the heading, unique within its page, and stable when
  the heading changes (only set when empty).
- [x] `OfferingService.home_cards()`: published services with `show_on_home`, ordered, at most
  six.
- [x] `OfferingService.all()`: every published service, ordered; each has a unique anchor.
- [x] `TeamService.leadership()`: published members, ordered.
- [x] `PartnerService.partners()` / `.clients()` split by `kind`, published only.
- [x] `seed_site_content` is idempotent: running it twice leaves the same row counts.

### 3.5 Users (`users.md` §8)

- [x] Both adapters' `is_open_for_signup` return `False`; the sign-up URL offers no form.
- [x] Google login: an existing active user's email → signed in; an unknown email → refused; an
  inactive user → refused.
- [x] `UserService.onboard_user` lower-cases the email, generates a unique username, sets an
  unusable password and sends the set-password email.
- [x] A Content Editor can change pages, sections, slides, services, team and partners, view
  submissions, and **cannot** see users or groups.
- [x] The admin is not at `/admin/` with prod settings when `ADMIN_URL_PATH` is set.

### 3.6 Controller smoke tests

Status code, template and one expected string for each:

- [x] `/`, `/about/`, `/services/`, `/contact/` → 200 (`apps/core/tests/test_consent.py`).
- [ ] `/sitemap.xml` (lists the four pages, not the admin), `/robots.txt` (points to the
  sitemap) → 200.
- [ ] An unknown URL → the branded 404.
- [ ] A seeded old URL (for example `/about-us/`) → 301 to its new page.
- [ ] Each page's `<title>`, meta description and canonical are present and unique.
- [x] No `googletagmanager` or `maps.googleapis`/`google.com/maps/embed` URL appears in the
  initial HTML of any page (both are injected by JavaScript after consent).

### 3.7 Security settings

- [ ] `check --deploy` with prod settings prints no warnings beyond the two deliberately silenced
  ones, `security.W005` and `W021` (`apps/core/tests/test_security.py`).
- [ ] Prod settings: `DEBUG=False`, secure cookies, HSTS, `SECURE_SSL_REDIRECT`,
  `X-Frame-Options: DENY`, `nosniff`, referrer policy.

## 4. Manual QA checklist (Day 9 and Day 10)

Run on the local prod stack (Day 9) and again on the preview host (Day 10).

**Pages**
- [ ] Home, About, Services and Contact at 375, 768 and 1280 px: no sideways scroll, no
  overlapping text, images sharp.
- [ ] The hero slider pauses on hover and focus, its controls work by keyboard, and it doesn't
  auto-advance with reduced motion on.
- [ ] Services anchor links scroll to each of the 13 services; the long bios collapse on mobile.
- [ ] Every top-bar and footer value matches `SiteSettings`; empty social URLs show no icon.

**Enquiries**
- [ ] Contact form with JavaScript on: success message; the enquiry is in the admin and the
  mailbox; replying in the mailbox addresses the visitor.
- [ ] Contact form with JavaScript off: same result through a full-page POST.
- [ ] Services enquiry block: in the admin with source "services".
- [ ] With a deliberately wrong `RESEND_API_KEY` (local only): the visitor still sees success,
  the admin shows **Email sent: No** with the error, and "Resend notification email" works once
  the key is fixed.

**Consent**
- [ ] First visit: the banner shows; the network tab shows no request to Google.
- [ ] Decline: still no Google requests after a reload; the map shows the address and the
  directions link.
- [ ] Accept: GA4 loads, the map loads; the footer link reopens the choice.

**Admin**
- [ ] A Content Editor edits a Home section, reorders a slide, adds a team member with a photo,
  and sees each change on the site.
- [ ] Image uploads show on the site (served by Caddy from the media volume in prod).
- [ ] Google sign-in works for an existing user and refuses an unknown account.

**Go-live (Day 10)**
- [ ] Valid certificate on the preview host, then on `distinctive.co.zw` and `www`.
- [ ] `http://` redirects to `https://`; `www` and the apex agree on one canonical host.
- [ ] Every URL from the old sitemap answers 301 to a live page.
- [ ] Mail to `enquiries@distinctive.co.zw` still arrives after the DNS change.
- [ ] Lighthouse on the live domain: Performance ≥ 90, Accessibility ≥ 90, SEO ≥ 95.
- [ ] Keyboard-only: skip link, nav, slider, cookie banner, both forms.
