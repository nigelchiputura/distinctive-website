# Testing Strategy

**Project-wide · revised 2026-11-02** (renamed from `testing.md`; the required cases now live in
each phase's `Test_Plan.md`; CI gate aligned with Consult 360)

## 1. Philosophy

A content site with a few places where a mistake is costly: HTML sanitising, contact submissions
(never lose one), hiding unpublished content, and in Phase 2 the job rules and search. Testing
effort follows that risk:

1. **The service layer is the gate.** Fast, database-free unit tests with fake repositories (and
   a fake mailer). CI fails if they fail or if service coverage drops below 85%.
2. **Security-sensitive behaviour is tested as seriously as rules:** the Markdown sanitiser,
   CSRF, the honeypot and rate limit, `check --deploy`.
3. **A few repository tests** where the query itself is the logic (published filters; in
   Phase 2, open jobs and full-text search).
4. **Light controller smoke tests:** every URL returns the right status, template and one
   expected string.
5. **A dedicated search suite in Phase 2,** against real Postgres.
6. **No browser E2E.** Layout and consent behaviour are covered by the manual QA checklist and
   Lighthouse; Phase 2's highlighting gets a small JS unit test.

## 2. Tooling

| Tool | Use |
|---|---|
| `pytest` + `pytest-django` | Runner |
| `pytest-cov` | Coverage; `.coveragerc` measures `apps/*/services/*` |
| Plain helper functions (or `factory_boy` if it earns its place) | Test data for DB tests |
| `ruff` | Lint |
| `basedpyright` (standard mode, `tests/` excluded) | Type check; tests are excluded so duck-typed fakes need no `Protocol` |
| Django's `mail.outbox` and a fake mailer | Email without sending |
| Node `--test` (Phase 2, dev and CI only) | Unit test for `highlight.js` |

`config/settings/test.py` uses Postgres (the CI service container, or the compose `db` locally),
not SQLite, so behaviour matches production, and a fast password hasher
(`MD5PasswordHasher`), which Consult 360 found makes user-heavy tests much quicker.

## 3. Test layers

### 3.1 Service tests (mandatory, no DB)

Services receive a fake repository:

```python
class FakePageRepo:
    def __init__(self, pages): self.pages = {p.slug: p for p in pages}
    def get_published_by_slug(self, slug): return self.pages.get(slug)
    def published_sections(self, page): return [s for s in page.sections if s.is_published]

def test_unpublished_sections_are_hidden():
    svc = PageService(repo=FakePageRepo([about_page]))
    assert [s.heading for s in svc.get_page("about").sections] == ["Our Story"]
```

### 3.2 Repository tests (a few, real DB)

`BaseRepository` generics, `published()`, ordering and slug uniqueness; Phase 2 adds open jobs
and the search queries.

### 3.3 Controller smoke tests

Status code, template, one expected string per route; form behaviour (valid, invalid, honeypot,
rate limit, no-JS fallback).

### 3.4 Layering test

`apps/core/tests/test_layering.py` scans imports and source: it fails if a controller imports a
repository or `django.db.models`, or if a service file contains `.objects`. The architecture rule
is a CI rule.

## 4. What we deliberately don't test

- Bootstrap behaviour, Django internals, allauth internals.
- Pixel-level layout (the manual responsive checklist and Lighthouse cover it).
- The Google OAuth round trip (manual on each host; the adapter logic is unit tested).
- Resend itself (the fake mailer stands in; one real send is a manual check per environment).

## 5. Coverage and CI gate

| Area | Target |
|---|---|
| `apps/*/services/` | ≥ 85% line coverage (**the gate**: `--cov-fail-under=85`) |
| `MarkdownService`, `ContactService` | 100% of their branches (checked in review) |
| Phase 2 `apps/search/services/` | ≥ 90% (informational) |

CI order (`deployment.md` §5): `ruff` → `basedpyright` → `makemigrations --check` → `pytest`
with coverage, and `css-fresh` in parallel. Failing either job blocks the merge and the image
build.

## 6. Where the cases are

- `Phase_1/Test_Plan.md` §3: required tests for core, the sanitiser, contact, content, users,
  smoke and security; §4: the manual QA checklist, including go-live.
- `Phase_2/Test_Plan.md` §3: jobs, the search suite, highlighting; §4: manual QA.
