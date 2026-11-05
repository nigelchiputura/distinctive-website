# Phase 2 — Task Breakdown (draft, about 8 working days)

**Status:** Draft 2026-11-02 · revised and agreed at kickoff (`Phase_Gates.md` §4) · scope:
`Phase_2/Phase2_Scope.md`

The same standing practices as Phase 1 (`Phase_1/Task_Breakdown.md`, top). Day numbers restart
at 1. There is no fixed deadline; the day order is what matters.

---

## Day 1 — Jobs model, rules and admin

- [ ] **App and model.** `apps/jobs` with `JobPosting` (`Phase2_Scope.md` J1); migration.
  AC: migration applies; slug unique.
- [ ] **Layers.** `JobRepository.open(today)`, `get_open_by_slug`, `recent(n)`;
  `JobService.list_open_jobs(page)`, `get_open_job(slug)`, `recent_jobs()`.
  AC: the JobService tests in `Phase_2/Test_Plan.md` §3.1 pass.
- [ ] **Admin.** EasyMDE vendored into `static/vendor/easymde/` via `copy-vendor.mjs`;
  filters, closing date in the list, apply email prefilled from `SiteSettings`; Content Editor
  group gains the jobs permissions (data migration).
  AC: an editor writes a posting in Markdown with a preview.

**Done when:** an editor can create and publish a posting, and the rules are tested.

## Day 2 — Jobs pages and SEO

- [ ] **List and detail.** `JobListController`, `JobDetailController`, templates and cards
  (`Phase2_Scope.md` J3–J5); `static/scss/pages/_jobs.scss`.
  AC: open jobs listed and paginated; a closed job's URL shows the closed page with 404.
- [ ] **Navbar and Contact.** Jobs added to the nav list; the vacancies line links to `/jobs/`.
  AC: the nav shows Jobs on every page.
- [ ] **SEO.** `JobPosting` JSON-LD; open jobs in the sitemap.
  AC: Google's Rich Results Test accepts a posting.
- [ ] **Redirects.** Re-point the Phase 1 job redirects to `/jobs/` or the new posting.
  AC: every old job URL answers 301 to a live page.
- [ ] **Seed.** `seed_site_content` gains the old site's current postings (if any are still
  open).

**Done when:** Jobs is complete and linked from the nav.

## Day 3 — Search index

- [ ] **App and model.** `apps/search` with `SearchEntry`, the GIN index, and a migration test
  that the index exists.
- [ ] **Indexing.** `to_search_entry()` on `PageSection`, `Service`, `TeamMember`,
  `JobPosting`; `SearchIndexService.sync` / `.remove`; signals; `SearchRepository.upsert` /
  `.delete`.
- [ ] **Rebuild.** `rebuild_search_index` (idempotent, removes orphans); entrypoint hook;
  `close_expired_jobs` run nightly from the VPS cron (or folded into the rebuild).
  AC: the indexing and visibility cases in `Phase_2/Test_Plan.md` §3.2 pass.

**Done when:** every searchable record has a correct, up-to-date entry.

## Day 4 — Search queries and endpoints

- [ ] **SearchService.** `suggest(q)` (prefix, top 6, min length, sanitised terms) and
  `search(q, page)` (ranked, headlines, paginated).
- [ ] **Controllers.** `/search/suggest/?q=` (JSON envelope) and `/search/?q=` (results page).
  AC: the matching, ranking, dropdown and results cases in §3.2 pass.

**Done when:** the whole search suite passes against Postgres.

## Day 5 — Search dropdown and results page

- [ ] **Navbar search.** Input and icon in `_navbar.html`; `search-dropdown.js`
  (`Phase2_Scope.md` §2.2); `_search.scss`.
- [ ] **Results page.** Type badges, snippets, pagination, empty state with links to Services
  and Contact.
  AC: keyboard-only use works (↑ ↓ Enter Esc); screen readers announce the result count.

**Done when:** typing finds content from every page, and Enter opens the results page.

## Day 6 — Highlighting

- [ ] **`highlight.js`** and its toolbar (`Phase2_Scope.md` §2.2).
- [ ] **JS unit test** for the wrapping function (Node `--test`, dev-only, run in the
  `css-fresh` job's Node step).
  AC: the highlighting cases in `Phase_2/Test_Plan.md` §3.3 pass.

**Done when:** clicking a result lands on the page with every match highlighted.

## Day 7 — Hardening and QA

- [ ] Fill test gaps; coverage gate holds.
- [ ] Lighthouse on Home, Services, Jobs and the results page.
- [ ] The manual QA checklist in `Phase_2/Test_Plan.md` §4.
- [ ] Decide on the backlog items the client wants next (`Phase2_Scope.md` §6).

**Done when:** QA is ticked and Lighthouse targets hold.

## Day 8 — Deploy and handover

- [ ] Deploy with the `Deploy VPS` workflow; check `rebuild_search_index` ran in the logs.
- [ ] Client walkthrough: posting a job, closing it, searching for it.
- [ ] Update `docs/Operations.md` (jobs, search rebuild, the nightly job).
- [ ] **Phase 2 gate** (`Phase_Gates.md` §3).

**Done when:** Jobs and Search are live and the gate is affirmed.
