# Development Conventions

**Project-wide · applies in every phase**

How work on the Distinctive website is done and handed over, whoever is doing it: the developer,
Claude in claude.ai, or Claude Code. `../CLAUDE.md` at the repo root holds the same rules in
short form, because Claude Code reads that file automatically at the start of every session.
**When a rule changes, change it in both files in the same piece of work.**

These are the conventions used on Consult 360, carried over unchanged except where this project
differs (no tenancy, no interfaces, no theming).

## 1. Phase discipline

1. **Work only on the current phase.** Its status is in `Phase_Gates.md` §1 and its cards are in
   `Phase_N/Task_Breakdown.md`. No next-phase code is written early, even if it looks quick.
   In Phase 1 that means no Jobs or Search code.
2. **Affirm a phase before moving on.** When the last card is done, work through
   `Phase_Gates.md` §3 and state either **"Phase N build complete."** with the evidence, item by
   item, or **"Phase N not complete."** with exactly what is outstanding. The next phase's
   kickoff waits for "complete" and the owner's sign-off.
3. **Scope discipline.** Anything well beyond the current phase is left out and noted for later
   (in the phase's scope doc or the backlog). A small item that uses existing data or logic can
   be done now.

## 2. Days

Each phase is planned as numbered days (`Phase_N/Task_Breakdown.md`). A day is finished when its
**Definition of Done** holds **and** its commands file exists (§3.2). Day numbers restart at 1 in
each phase, and are sequence, not calendar dates.

Every day: work in a branch, open a PR, merge only when CI is green.

## 3. Handing work over

### 3.1 Say where every file goes

For every file created or changed, say where it goes in the repo, and which commands it needs
(migrations, `npm run build:css`, tests, a rebuild).

### 3.2 Write the day's commands file

When a day's tasks are completed, write `commands/Phase_N/day-M.md`: every terminal command to
run after that day's code is in place, in order, each with what it should print. The format
rules are in `commands/README.md`:

- run from the repo root;
- PowerShell and bash forms where they differ;
- one-time steps marked;
- complete, so the file doesn't depend on reading the earlier days' files;
- written in Markdown: a `##` heading per step, commands in fenced `bash` or `powershell`
  blocks, and an **Expect:** line after each.

Add the file's row to the index in `commands/README.md`. If a later fix changes a day's
commands, edit that day's file and its "Revised" line rather than starting a new file.

## 4. Errors

Log every non-trivial error in `errors-and-exceptions/<slug>__<YYYY-MM-DD_HHMM>/` with
`error_details.md` and `error_resolution.md`, and add a row to `errors-and-exceptions/README.md`.
The process and the "is it non-trivial?" guideline are in `Errors_And_Exceptions.md`. Logging is
part of finishing the card the bug interrupted, not a separate card.

## 5. Documentation

When scope or design changes, update **every** affected document in the same piece of work:
the phase scope doc, `architecture.md`, `folder_structure.md`, `frontend.md`, `deployment.md`,
`users.md`, the test plans, and this file. References between documents are written relative
to `docs/`. Where documents live: `Phase_Gates.md` §5.

## 6. Architecture

From `architecture.md`:

- Model → Repository → Service → Controller → View.
- Controllers never import repositories or use the ORM; services never call `Model.objects`.
  `apps/core/tests/test_layering.py` makes this a CI rule.
- **No interfaces.** Services take their repository through the constructor with a real
  default (`repo or JobRepository()`), and tests pass a plain duck-typed fake. `tests/`
  folders are excluded from basedpyright so fakes don't need a `Protocol`.
- The only documented exceptions: the Django admin, data migrations and management commands
  may use the ORM; signals call a service, never the ORM.

## 7. Frontend

From `frontend.md`:

- SCSS is compiled locally with `npm run build:css`, and the compiled `static/css/main.css` is
  committed. CI's `css-fresh` job rejects stale CSS and source-map references.
- **No Node in any image or on any server.** The dev image installs `dev.txt`, whose
  basedpyright package bundles a Node runtime inside site-packages. That copy is for type
  checking only, is not on the PATH, and is never shipped.
- Colours only through brand tokens (`$dcs-*` / `var(--dcs-*)`).
- HTML from admin-entered text only through `MarkdownService` (sanitised with `nh3`).
- Template comments: `{# … #}` for one line only; anything longer is `{% comment %} … {% endcomment %}`.
  A `{#` closed on a later line isn't a comment, and tags inside it run
  (`errors-and-exceptions/multiline-template-comment-recursion__2026-11-03_1135/`; a test enforces it).

## 8. Local Docker

- **Always start with `--build`**:
  `docker compose -f docker/docker-compose.yml up --build`. The source is bind-mounted, but the
  Python packages live in the image. If `requirements/` changes and the image isn't rebuilt, the
  entrypoint stops with a clear message (`deployment.md` §2.1).
- Requirements only grow: `base.txt` → `prod.txt` → `dev.txt`, and each includes the one before.
  Every image variant can then run every Dockerfile step.
- `down -v` deletes the local Postgres and media volumes. Never run it against anything but
  local data.

## 9. Working in Claude Code

The rules above apply unchanged. In addition:

- Claude Code can run commands itself. It runs the day's checks (tests, ruff, basedpyright,
  `makemigrations --check`, `npm run build:css`, Docker where available) and reports the
  results. It still writes the commands file, because the owner re-runs those steps on their
  own machine.
- Steps only the owner can do are listed for the owner, not attempted:
  - pushing to `main`;
  - GitHub settings and secrets;
  - VPS, DNS, Resend, Google Cloud and GA4 configuration;
  - anything touching the live site or real enquiries.
- Claude Code commits only when asked, and never pushes to `main` without being told to.
