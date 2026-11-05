# Phase 1 Scope — Live brochure site

**Status:** Agreed 2026-11-02 · **Length:** 10 working days · **Client:** Distinctive Consultancy
Services

The single source of truth for what Phase 1 delivers, the decisions behind it, and what is left
for Phase 2. Every Phase 1 document follows it. If they ever disagree, this one wins, and the
other document gets fixed.

## 1. Why there are two phases

The original plan was one 15-day build ending in a Render demo. The client wants **something
visual now**, so the build is split:

- **Phase 1** ships the pages that are static or mostly static (Home, About, Services, Contact),
  already admin-editable, **live on `distinctive.co.zw`**, replacing the WordPress site.
- **Phase 2** adds the pages that need more care (Jobs and site-wide Search), at the owner's
  own pace, deployed to the same server when ready.

Phase 1 builds the foundation Phase 2 needs (the layers, the base classes, the content models
with section anchors, the deployment), so Phase 2 adds apps without reworking Phase 1.

## 2. Decisions

| # | Decision | Decided |
|---|---|---|
| **D1** | Django SSR, Postgres, Docker in development and production, data on Docker volumes. | 2026-10-07 |
| **D2** | **Model → Repository → Service → Controller → View**, with **no interfaces**: services take their repository through the constructor with a real default, and tests pass duck-typed fakes (`architecture.md` §3). | 2026-10-07 |
| **D3** | Bootstrap 5 customised through SCSS, compiled with **Dart Sass via npm on the dev machine**; the compiled CSS is committed; CI's `css-fresh` job fails on stale CSS. No Node in any image or on any server. | 2026-10-07 |
| **D4** | Page content is **admin-editable from the start**: page sections, hero slides, services, team, partners/clients, site settings. Nothing the client might edit is hard-coded in a template. | 2026-10-07, confirmed for Phase 1 on 2026-11-02 |
| **D5** | Admin bodies are **Markdown**, rendered to sanitised HTML (`markdown` + `nh3`) in one place only. | 2026-10-07 |
| **D6** | `User(AbstractUser)`, email login, **no public sign-up**; admins onboard users; **Google login for existing users only**, no domain restriction; Jazzmin admin. | 2026-10-07 |
| **D7** | Contact submissions are **saved, then emailed** to `enquiries@distinctive.co.zw`. The Services page "Get In Touch" block is a general enquiry form on the same service, tagged with its source page. | 2026-10-08 |
| **D8** | **Email goes through Resend's HTTPS API** via `django-anymail`, the same provider and setup as Consult 360. Replaces the earlier Brevo plan. The provider stays a setting (`EMAIL_PROVIDER`). | 2026-11-02 |
| **D9** | **Uploaded images use local storage**: a Docker volume on the VPS, served by Caddy at `/media/`. Cloudflare R2 is deferred (Phase 2 backlog). | 2026-11-02 |
| **D10** | **Phase 1 goes live on a VPS at `distinctive.co.zw`** (Docker Compose + Caddy), first at a preview hostname for the client walkthrough, then cut over. There is **no Render demo** in this project. | 2026-11-02 |
| **D11** | Phase 1 pages: **Home, About, Services, Contact**. Jobs and Search are Phase 2. The navbar shows only built pages; the search icon arrives with Search. | 2026-11-02 |
| **D12** | SEO basics (meta, Open Graph, JSON-LD `Organization`, sitemap, robots), a cookie banner, and **GA4 loaded only after consent**. The Google Map is an interactive Maps Embed iframe, also loaded only after consent. | 2026-10-08 |
| **D13** | Social icons: Facebook, LinkedIn, Instagram, X, each a `SiteSettings` URL shown only when filled in. RSS dropped. | 2026-10-08 |
| **D14** | Old WordPress URLs get **301 redirects** to their new pages, so links and search rankings survive the cutover. | 2026-11-02 |

## 3. Phase 1 deliverables

### 3.1 Platform

| # | Deliverable |
|---|---|
| F1 | Repo, split settings, Docker (dev and prod variants of one image), Postgres volume, entrypoint with the requirements fingerprint check. |
| F2 | CI: `ruff`, `basedpyright`, `makemigrations --check`, `pytest` with the 85% services coverage gate, `css-fresh`; image built and pushed to GHCR on `main`. |
| F3 | `apps/core`: base model and mixins, `BaseRepository`, `BaseService`, `BaseController`, the `ServiceError` family, `SiteSettings`, `MarkdownService`, `SeoMixin`, layering test, start-up checks for email settings, `LOGGING`. |
| F4 | Users and admin: custom `User`, allauth (password + Google), sign-up closed, Content Editor group, Jazzmin branding, admin at `ADMIN_URL_PATH`. |
| F5 | Production on a VPS: `docker-compose.prod.yml` (web, db, caddy), `Caddyfile`, `.env.prod.example`, manual `deploy-vps.yml` workflow, nightly backups of the database **and** the media volume. |

### 3.2 Pages (`frontend.md` §4)

| # | Page | Content |
|---|---|---|
| P1 | Global | Top bar, navbar (Home, About Us, Services, Contact Us), footer "Reach Us", all from `SiteSettings` |
| P2 | Home | Hero slider (3 slides), six service cards (`Service.show_on_home`), "Get In Touch" CTA, People Centred and Proactive value blocks |
| P3 | About | Hero, Our Story, Strategic Partners, Capability Analysis, Value Driven and Capacity Building, Our Leadership (8 people) |
| P4 | Services | Static hero + anchor nav, "What We Do", 13 alternating service bands, NGO Capacity Development diagram, corporate-clients logo grid, enquiry block |
| P5 | Contact | AJAX contact form with no-JS fallback, "Reach Us" panel, consent-gated Google Map |
| P6 | Cross-cutting | SEO, sitemap, robots, cookie banner, GA4 after consent, 404/500 pages, 301 redirects from old URLs, Lighthouse targets |

### 3.3 Content

`seed_site_content` loads the old site's real content (page text, services, team bios,
partners, clients, contact details) so the live site launches complete, not empty. Images are
taken from the old site's media library with the client's agreement.

## 4. Deferred to Phase 2 (`Phase_2/Phase2_Scope.md`)

| # | Deferred | Why not now |
|---|---|---|
| L1 | **Jobs**: list, detail, Markdown postings, closing dates, apply by email or link, `JobPosting` JSON-LD | Needs its own model, rules (open vs closed), admin editor and SEO; the client asked for visuals first |
| L2 | **Search**: unified Postgres FTS index, navbar dropdown, results page, highlighting on arrival | The one complex feature; it's best built once all content types exist (it indexes jobs too) |
| L3 | Cloudflare R2 for media | Local storage on the VPS is enough at this content size |

**What Phase 1 does so Phase 2 slots in:** every `PageSection` and `Service` has a stable
`anchor` slug from Phase 1 (search results will link to `#anchor`); the navbar is built from a
list in the context processor, so Jobs and the search icon are one entry each; `TeamMember`,
`Service` and `PageSection` keep plain-text-friendly fields so `to_search_entry()` can be added
without migrations beyond the search app's own.

## 5. Assumptions the build makes

| # | Assumption |
|---|---|
| A1 | The enquiries mailbox already exists and keeps working through the cutover. Only the website's `A`/`AAAA`/`www` records change; **MX and existing mail records are untouched**. |
| A2 | The Resend account used for CVision verifies a sending subdomain of `distinctive.co.zw` (for example `mail.distinctive.co.zw`), and the website sends from it. |
| A3 | Until Phase 2, there is **no Jobs page**. The Contact page's "Reach Us" panel shows a vacancies line ("Send your CV to recruitment@…", from `SiteSettings.recruitment_email`), and old job URLs 301 to `/contact/`. |
| A4 | Brand colours are the values eyeballed from the screenshots (`frontend.md` §2) until the logo file confirms them. |
| A5 | Content is English only. |

## 6. Questions open with the client or owner

| # | Question | Needed by | Default if unanswered |
|---|---|---|---|
| Q1 | Does the client post jobs often enough that the Jobs page must be live in Phase 1? | Day 1 | A3: no Jobs page; vacancies line on Contact |
| Q2 | Which VPS? (Consult 360's comparison recommends Vultr Johannesburg, 1 vCPU / 2 GB, about $12/month.) Could it share a server with Consult 360 or CVision? | Day 9 | A dedicated Vultr Johannesburg 2 GB server |
| Q3 | Who controls `distinctive.co.zw` DNS? The CVision notes say Cloudflare; confirm and get access. | Day 7 (Resend), Day 10 (cutover) | Cloudflare |
| Q4 | Where is the `enquiries@` mailbox hosted (Google Workspace, the WordPress host's cPanel mail, other)? This matters only to keep its MX records intact at cutover. | Day 10 | Leave every mail record as is |
| Q5 | Exact brand colours and the logo in SVG or high-resolution PNG; the original photos for Home (the hero team photo without text over it, the six service-card images, the two value-block images) | Day 2 (logo), Day 9 (photos) | A4; Home uses images cut from the old site's screenshots and a hero without a photo |
| Q6 | Who at Distinctive edits content, and do they want Google sign-in? | Day 4 | One superuser plus one Content Editor |
| Q7 | Keep the "Designed by" footer credit? | Day 2 | Removed |
| Q8 | Is the WordPress host contract ending, and is a full backup of the old site (files + database) taken before cutover? | Day 10 | The owner takes a backup on Day 9 |

## 7. Prerequisites (owner, outside the code)

| Item | Needed by |
|---|---|
| GitHub repository (private) and Actions enabled | Day 1 |
| Logo files and brand colours (Q5) | Day 2 |
| Google Cloud OAuth client (Web) with redirect URIs for localhost, the preview host and the live domain | Day 4 |
| Old-site content: page text, team bios and photos, partner and client logos, service images (export from WordPress or copy from the live site) | Day 5 |
| Resend sending domain verified (DNS records on `distinctive.co.zw`) and a Sending-access API key | Day 7 |
| Google Maps Embed API key, restricted by HTTP referrer to the preview host and the live domain | Day 8 |
| GA4 property and measurement ID | Day 8 |
| The old site's URL list (its `wp-sitemap.xml` or `sitemap_index.xml`) for the redirect map | Day 9 |
| VPS ordered, SSH key added, Docker installed (`deployment.md` §7) | Day 9 |
| DNS access for the preview record and the cutover (Q3) | Day 10 |

## 8. Capacity

**10 working days** (`Phase_1/Task_Breakdown.md`). The days are tight but the scope is the
mostly-static half of the site. If a day slips, the cutover moves, not the quality bar: the
client can walk through the preview host while the last cards finish.
