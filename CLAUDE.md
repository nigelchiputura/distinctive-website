# Working conventions for the Distinctive website

Read this first in every session. It records how the project owner wants work done. The full
version, with the reasons, is `docs/Development_Conventions.md`. **When a rule changes, change it
in both files.**

## Where things are

- `docs/README.md`: the index of every document.
- `docs/Phase_Gates.md`: which phase we are in, and how a phase is closed.
- `docs/Phase_N/`: the scope, task breakdown and test plan of each phase.
- `docs/commands/Phase_N/day-M.md`: the commands to run after each completed day.
- Project-wide docs live in `docs/`. Document references are written relative to `docs/`.

## Rules

1. **Work only on the current phase.** Check its status in `docs/Phase_Gates.md` §1 and its
   cards in `docs/Phase_N/Task_Breakdown.md`. Don't start next-phase work early (no Jobs or
   Search code during Phase 1).
2. **Affirm a phase before moving on.** When the last card is done, work through
   `docs/Phase_Gates.md` §3 and state either "Phase N build complete." with the evidence, or
   "Phase N not complete." with what is outstanding. Kickoff of the next phase waits for
   "complete" and the owner's sign-off.
3. **For every file you create or change, say where it goes and which terminal commands to run**
   (migrations, `npm run build:css`, tests, a rebuild).
4. **Write the day's commands file.** When a day's tasks are completed, write
   `docs/commands/Phase_N/day-M.md`:
   - every command to run after that day's work, in order, run from the repo root, each with
     what it should print;
   - PowerShell and bash forms where they differ;
   - one-time steps marked;
   - complete on its own;
   - Markdown: a `##` heading per step, commands in fenced `bash` / `powershell` blocks, and an
     **Expect:** line after each.

   Add its row to `docs/commands/README.md`. If a later fix changes a day's commands, edit that
   file and its "Revised" line. A day isn't done until this file exists.
5. **Log every non-trivial error** in `docs/errors-and-exceptions/<slug>__<YYYY-MM-DD_HHMM>/`
   with `error_details.md` and `error_resolution.md`, and add a row to that folder's
   `README.md` index (`docs/Errors_And_Exceptions.md`).
6. **Scope discipline.** If something goes well beyond the current phase, leave it out and note
   it for later. If it is small and uses existing data or logic, it can be done now.
7. **Keep docs consistent.** When scope or design changes, update every affected document in
   the same piece of work.
8. **Architecture rules** (`docs/architecture.md`):
   - Model → Repository → Service → Controller → View.
   - Controllers never touch repositories or the ORM; services never call `Model.objects`.
     `apps/core/tests/test_layering.py` enforces it.
   - **No interfaces / `Protocol`s.** Services take their repository through the constructor
     with a real default; tests pass a duck-typed fake. Tests are excluded from basedpyright.
9. **Frontend rules** (`docs/frontend.md`):
   - SCSS is compiled locally with `npm run build:css`, and the compiled CSS is committed.
   - No Node in any image or on any server. Node runs on the dev machine and in CI's
     `css-fresh` job only.
   - Colours only through the brand tokens (`$dcs-*` in SCSS, `var(--dcs-*)` in CSS).
   - Markdown becomes HTML only through `MarkdownService` / the `{% markdown %}` filter.
10. **Local Docker:** always `docker compose -f docker/docker-compose.yml up --build`. The
    source is bind-mounted, but the packages live in the image.

## In Claude Code

- Run the day's checks yourself and report the results:
  - `pytest --cov=apps --cov-config=.coveragerc --cov-fail-under=85`;
  - `ruff check .`, `ruff format --check .`, `basedpyright`, `python manage.py makemigrations --check --dry-run`;
  - `npm run build:css`, then confirm `git status` shows no CSS change.
- Still write the commands file (rule 4), because the owner re-runs those steps on their own
  machine.
- Leave these to the owner, and list them for the owner:
  - pushing to `main`;
  - GitHub settings and secrets;
  - VPS, DNS, Resend, Google Cloud and GA4 configuration;
  - anything touching the live site or real enquiries.
- Commit only when asked.
