# Phase 2 Scope — Jobs and Search

**Status:** Draft 2026-11-02 · agreed at kickoff after the Phase 1 gate (`Phase_Gates.md` §4) ·
**Pace:** the owner's own; no fixed deadline

Phase 2 adds the two features that need more attention than the brochure pages: **Jobs** and
**site-wide Search**. Both are deployed to the same VPS as Phase 1, with no change to the
deployment. The designs below move into `architecture.md` and `frontend.md` as they are built.

## 1. Decisions carried in (agreed 2026-10-07/08)

| # | Decision |
|---|---|
| **E1** | Job postings: title, department, location, employment type, **closing date**, Markdown description, optional image (with a default banner), `apply_email` and/or `apply_url`, published flag. **No on-site applications or CV uploads.** |
| **E2** | Only **open** jobs are listed: published, and the closing date is today or later (a job closing today is still open). |
| **E3** | **Search** is Postgres full-text search over one unified index (`SearchEntry`), covering page sections, services, team members and open jobs. |
| **E4** | Search UX: a **live AJAX dropdown** as you type, plus a full **results page** on Enter. Arriving on a page from a result highlights every match with next/previous controls. |
| **E5** | Search is built on the Phase 1 anchors: each result links to `/<page>/?q=<term>#<anchor>`. |

## 2. Deliverables

### 2.1 Jobs

| # | Deliverable |
|---|---|
| J1 | `apps/jobs`: `JobPosting(BaseModel, PublishableMixin, SluggedMixin)`; `JobRepository.open(today)`, `get_open_by_slug`, `recent(n)`; `JobService.list_open_jobs(page)`, `get_open_job(slug)`, `recent_jobs()` |
| J2 | Admin: EasyMDE Markdown editor (vendored, no CDN) on the description; filters for department, employment type, open/closed; closing date in the list |
| J3 | `/jobs/`: "Listed Jobs" card grid (image, title, excerpt, department, location, type, closing-date badge), numbered pagination, empty state ("No open vacancies; send your CV to …") |
| J4 | `/jobs/<slug>/`: banner, metadata, sanitised Markdown body, "How to apply" block from `apply_email`/`apply_url`, sidebar with recent postings |
| J5 | Closed or unpublished job URL → **410-style "This vacancy has closed" page with status 404**, linking to `/jobs/` (decision on Phase 2 Day 2 if the client prefers a plain 404) |
| J6 | `JobPosting` JSON-LD (`datePosted`, `validThrough`, `employmentType`, `hiringOrganization`, `jobLocation`); open jobs in `sitemap.xml` |
| J7 | Navbar gains **Jobs**; the Phase 1 vacancies line on Contact links to `/jobs/`; the Phase 1 redirects for old job URLs are re-pointed from `/contact/` to `/jobs/` (or to the matching new posting) |

### 2.2 Search

**Index.**

```
SearchEntry
  source_type     page_section | service | team_member | job
  source_id
  title
  body            plain text (Markdown rendered then stripped)
  url             canonical page URL
  anchor          #fragment of the section or card
  is_public       false when the source is unpublished or the job is closed
  search_vector   SearchVectorField, GIN index, weighted (title A, body B)
```

- Each searchable model implements `to_search_entry()`. `post_save` / `post_delete` signals call
  `SearchIndexService.sync(instance)` / `.remove(instance)`, which go through
  `SearchRepository` (signals never touch the ORM).
- `rebuild_search_index` rebuilds everything and removes orphans. It runs in the entrypoint on
  every start (idempotent and cheap at this size), and a nightly job flips jobs whose closing
  date passed to `is_public=False`.

**Queries.**

- **Dropdown:** prefix matching with the `simple` configuration (`recr` finds "recruitment"),
  top 6, minimum 2 characters, terms sanitised before building the `tsquery` so `& | ! ' : * ( )`
  can't cause a syntax error.
- **Results page:** `websearch_to_tsquery('english', …)` with `SearchRank`; `SearchHeadline`
  snippets (escaped, then only the headline markers turned into `<mark>`); paginated.

**Endpoints.** `GET /search/suggest/?q=` (JSON envelope) and `GET /search/?q=` (results page).

**Frontend.** `search-dropdown.js` (debounce 250 ms, abort in-flight requests, ARIA combobox,
↑ ↓ Enter Esc, "See all results" row), results page with type badges and an empty state,
`highlight.js` (TreeWalker over `<main>`, `<mark class="search-hit">`, scroll to the first,
count + prev/next and `n`/`p` keys, skips `script, style, input, textarea, mark`, idempotent).
Mobile: the search icon opens a full-width input in the collapsed navbar.

## 3. Deferred again (the backlog, §6)

Nothing in Phase 2 requires R2 or a change to the Phase 1 deployment.

## 4. Assumptions

| # | Assumption |
|---|---|
| B1 | Search covers public content only. Users and contact submissions are never indexed. |
| B2 | English stemming is enough (the content is English). |
| B3 | Job volume stays small (tens of postings), so pagination at 9 per page and the in-request indexing are fine. |

## 5. Questions to settle at kickoff

| # | Question | Default if unanswered |
|---|---|---|
| Q1 | Closed job URL: a "vacancy has closed" page or a plain 404? | The "closed" page, with status 404 |
| Q2 | Should closed jobs stay visible in an "archive" for a while? | No |
| Q3 | Default apply address: `recruitment@distinctive.co.zw`? | Yes, prefilled in the admin from `SiteSettings.recruitment_email` |
| Q4 | Does the client want job alerts or a "share this job" button? | No (backlog) |

## 6. Backlog (optional, built when the client needs it)

| # | Item | What it needs |
|---|---|---|
| K1 | **Cloudflare R2** for media (if the media volume or bandwidth becomes a concern) | `django-storages` S3 backend behind `STORAGE_BACKEND=s3`, a copy of the media volume into the bucket, a `media.` custom domain on Cloudflare DNS |
| K2 | Responsive images generated on upload (`srcset`) | Pillow thumbnails or `sorl-thumbnail` |
| K3 | News / blog | A new app; search would index it via `to_search_entry()` |
| K4 | On-site job applications with CV upload | Upload validation, private storage, data protection review (see the CVision work) |
| K5 | Multi-language | `django-modeltranslation` or similar |
| K6 | 2FA for admin users | `django-allauth` MFA |
| K7 | Zero-downtime deploys | Two web containers behind Caddy, or a blue/green switch |
