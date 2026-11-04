# Errors & Exceptions Log — Process

A permanent, versioned knowledge base of every non-trivial error met while building the
Distinctive website, kept for future reference and for learning the stack (Django, Docker,
Postgres, Sass/Bootstrap, allauth, the Model → Repository → Service → Controller → View
layering). It follows the same process as Consult 360. It is deliberately **separate from
GitHub Issues / the task board** (§4).

## 1. Where it lives

```
docs/
└── errors-and-exceptions/
    ├── README.md                          # chronological index of every entry (§5)
    ├── _templates/
    │   ├── error_details_TEMPLATE.md
    │   └── error_resolution_TEMPLATE.md
    ├── _example-entry__2026-01-01_0000/   # worked example, not a real error (§6)
    │   ├── error_details.md
    │   └── error_resolution.md
    └── <error-slug>__<YYYY-MM-DD_HHMM>/   # one folder per real logged error
        ├── error_details.md
        └── error_resolution.md
```

## 2. Folder naming convention

```
<error-slug>__<YYYY-MM-DD_HHMM>
```

- **`error-slug`**: short, lowercase, hyphenated, describes the *error*, not the fix:
  `docker-postgres-connection-refused`, `markdown-sanitizer-strips-links`,
  `css-fresh-fails-on-committed-css`, `resend-refuses-unverified-sender`.
- **`YYYY-MM-DD_HHMM`**: 24-hour local time (Africa/Harare) when the error was **first
  encountered**, not when it was resolved. A hard bug can span two days; the folder name shows
  when the trail started.
- Two underscores separate the slug from the timestamp.

**Trade-off:** slug-first folders sort by error type, not time. That's good for "have I hit this
before?" and bad for "what went wrong this week?", which is what the index (§5) is for.

## 3. What goes in each file

### `error_details.md`: written as close to the moment of the error as possible

The *problem*, before the solution is known: what was being attempted, the exact message or
stack trace, the environment (local Docker / CI / VPS preview / production), the layer or area
affected, steps to reproduce, the initial suspected cause, and the **Severity** and
**Layer/Area** tags (§8).

Write it while still confused. Once you know the answer it's easy to misremember the symptom as
"obviously" pointing at the cause, and a future you hitting something *similar but not
identical* needs the real, messy original symptom.

### `error_resolution.md`: written once it's fixed

The *confirmed* root cause, the fix, why it works, alternatives considered and rejected, how to
prevent recurrence (a test, a lint rule, a check, a docstring), and a short **"what this taught
me"** takeaway about the stack.

## 4. Why this is separate from GitHub Issues / the task board

| | Issues / task board | `errors-and-exceptions/` |
|---|---|---|
| Answers | "What needs doing, and is it done?" | "What went wrong, and why, in detail?" |
| Lifespan | Closed and forgotten | Permanent |
| Audience | Whoever manages the current day | Future-you, debugging something *similar* |
| Granularity | Task | Root cause and reasoning |

A task card links to its error folder rather than repeating the explanation.

## 5. The index (`errors-and-exceptions/README.md`)

A running table, most recent first. Add the row **when you write the two files**, not later:

```markdown
| Date | Error | Layer/Area | Severity | Folder |
|---|---|---|---|---|
| 2026-11-03 14:20 | Docker Postgres connection refused | Infra/Docker | Medium | [docker-postgres-connection-refused__2026-11-03_1420](./docker-postgres-connection-refused__2026-11-03_1420/) |
```

## 6. The worked example

`_example-entry__2026-01-01_0000/` is a filled-out example of both files, kept permanently so the
format never has to be reverse-engineered. Copy its structure; don't delete it.

## 7. When to log an error

Log it when **any** of these are true:

- It took real investigation (more than ~10–15 minutes of genuine confusion).
- It revealed something non-obvious about Django, Docker, Postgres, Sass/Bootstrap, allauth,
  Resend, Caddy, or the layering.
- You (in six months) or a teammate would plausibly hit it again.
- It affected a shared environment (CI, the VPS, production) rather than one machine.

Skip: syntax errors caught instantly by the editor or linter, typos, anything fixed in under a
minute with no "why did that happen" moment.

## 8. Severity and layer tags

Every `error_details.md` carries two classification fields, used for scanning the index.

- **Severity:** `Low` / `Medium` / `High` / `Critical`.
  **Critical** = broke CI or production, **lost or exposed a contact submission**, **allowed
  unsanitised HTML to render (XSS)**, exposed unpublished content, or (Phase 2) exposed closed or
  unpublished content in search.
- **Layer/Area:** one of `Model`, `Repository`, `Service`, `Controller`, `View`, `Infra/Docker`,
  `CI-CD`, `Deployment/VPS`, `DNS`, `Frontend/SCSS`, `Frontend/JS`, `Content/Markdown`, `Email`,
  `Auth/Allauth`, `Admin`, `SEO`, `Test`, `Documentation`; Phase 2 adds `Jobs` and `Search`. This
  mirrors the vocabulary in `architecture.md`, so patterns show (for example, "we keep hitting
  Email bugs" is a signal to revisit the email design).
