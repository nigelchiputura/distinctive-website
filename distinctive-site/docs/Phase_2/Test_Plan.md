# Phase 2 — Test Plan

**Status:** Draft 2026-11-02 · agreed at kickoff

Required tests and manual QA for Jobs and Search. Approach and gates: `Testing_Strategy.md`.

## 3. Required test cases

### 3.1 Jobs

`JobService` (fake repository):

- [ ] Open vs closed vs unpublished: only published jobs closing today or later are listed.
- [ ] Boundary: a job closing **today** is listed; one that closed yesterday isn't.
- [ ] Ordering (newest first, then closing date) and pagination (9 per page; an out-of-range
  page gives the last page).
- [ ] `get_open_job` on a closed or unpublished slug raises `NotFoundError`.
- [ ] A posting needs at least one of `apply_email` or `apply_url` (validation).

Repository (DB): `JobRepository.open(today)` honours `is_published` and `closing_date`.

Controllers: `/jobs/`, `/jobs/?page=2`, `/jobs/<open-slug>/` → 200; a closed slug → 404 with the
closed page; the detail's JSON-LD has `validThrough` equal to the closing date; open jobs are in
`sitemap.xml` and closed ones aren't.

Markdown: a posting body with `<script>` renders without it (the Phase 1 sanitiser suite covers
the rest).

### 3.2 Search (against Postgres, small fixture corpus)

The corpus: a page section, a service, a team member, an open job, a closed job, an unpublished
section.

| Area | Cases |
|---|---|
| Indexing | Creating, updating and deleting a source creates, updates and removes its entry; Markdown is stripped to plain text; URL and anchor are correct |
| Visibility | Unpublished sections, closed jobs and drafts never appear in suggestions or results; unpublishing removes the entry; a job whose closing date passes disappears after the nightly job |
| Matching | Exact word; stemmed variant on the results page ("recruit" finds "recruitment"); prefix in the dropdown ("recr"); multi-word; case-insensitive |
| Ranking | A title match outranks a body match; more occurrences rank higher; ties are stable |
| Cross-page | One query returns hits from Home sections, Services, About/Team and Jobs |
| Dropdown | At most 6 results; minimum length 2; empty or whitespace → empty list, no error; `& \| ! ' : * ( )` never raise a query syntax error |
| Results page | Pagination; the snippet contains the term; the empty state |
| Safety | Snippets are escaped: a section containing `<script>` text yields an escaped snippet with only `<mark>` added |
| Rebuild | `rebuild_search_index` is idempotent and removes orphans |
| Performance | The dropdown's query count is constant (no N+1); the GIN index exists |

### 3.3 Highlighting (JS unit test)

- [ ] Several matches in one text node and across nodes; case-insensitive.
- [ ] Regex-special characters in the term (`c++`, `(hr)`) match literally.
- [ ] `script`, `style`, `input`, `textarea` and existing `mark` elements are skipped.
- [ ] Links and inline markup keep working after wrapping.
- [ ] Running it twice doesn't double-wrap.

## 4. Manual QA checklist

- [ ] Post a job in the admin with Markdown headings and lists; it renders correctly; the apply
  link and email work.
- [ ] Set its closing date to yesterday: it leaves the list, the search results and the sitemap.
- [ ] Search from every page, including terms with `&` and quotes.
- [ ] Keyboard-only: the search combobox (↑ ↓ Enter Esc), the results page, the highlight
  toolbar (`n`/`p`).
- [ ] Mobile: the search icon opens the input in the collapsed navbar.
- [ ] Clicking a result scrolls to and highlights the match; prev/next move between matches.
- [ ] Lighthouse on Jobs and the results page: Performance ≥ 90, Accessibility ≥ 90, SEO ≥ 95.
