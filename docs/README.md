# Documentation index — Distinctive website

Start with `../CLAUDE.md` (the working rules), then `Phase_Gates.md` (where the project is).

**Current phase: Phase 1** (Home, About, Services, Contact, live on `distinctive.co.zw` in 11
working days, since Day 9's UI and components polish was added on 2026-11-04). Phase 2 (Jobs and Search) is a draft.

## Project-wide (kept current)

| Document | What it covers |
|---|---|
| [Development_Conventions.md](./Development_Conventions.md) | How work is done and handed over (the long form of `CLAUDE.md`) |
| [Phase_Gates.md](./Phase_Gates.md) | The phases, their status, the completion checklist, where docs live |
| [architecture.md](./architecture.md) | The five layers, base classes, request flow, content model |
| [folder_structure.md](./folder_structure.md) | Repository layout, app shape, naming, git hygiene |
| [frontend.md](./frontend.md) | npm/Sass pipeline, tokens, templates, page notes, JS modules, consent, light and dark themes, motion |
| [deployment.md](./deployment.md) | Docker image, env vars, CI, Resend, the VPS, go-live and cutover |
| [users.md](./users.md) | Custom user, allauth (password + Google), groups, Jazzmin |
| [Testing_Strategy.md](./Testing_Strategy.md) | Testing approach, tooling, coverage gate |
| [Errors_And_Exceptions.md](./Errors_And_Exceptions.md) | The error-log process; the log itself is [errors-and-exceptions/](./errors-and-exceptions/README.md) |
| [commands/README.md](./commands/README.md) | What to run after each completed day |
| `Operations.md` | Running the live site (written on Phase 1 Day 11) |

## Phase 1 — Agreed 2026-11-02

| Document | What it covers |
|---|---|
| [Phase_1/Phase1_Scope.md](./Phase_1/Phase1_Scope.md) | Decisions, deliverables, deferrals, assumptions, open questions, prerequisites |
| [Phase_1/Task_Breakdown.md](./Phase_1/Task_Breakdown.md) | Eleven days of cards with acceptance criteria |
| [Phase_1/Test_Plan.md](./Phase_1/Test_Plan.md) | Required tests (§3) and manual QA, including go-live (§4) |

## Phase 2 — Draft

| Document | What it covers |
|---|---|
| [Phase_2/Phase2_Scope.md](./Phase_2/Phase2_Scope.md) | Jobs and Search designs, questions, the backlog |
| [Phase_2/Task_Breakdown.md](./Phase_2/Task_Breakdown.md) | About eight days of cards |
| [Phase_2/Test_Plan.md](./Phase_2/Test_Plan.md) | Jobs, the search suite, highlighting, manual QA |

## Archive

| Document | Why archived |
|---|---|
| [archive/task_breakdown__15-day-plan__superseded_2026-11-02.md](./archive/task_breakdown__15-day-plan__superseded_2026-11-02.md) | The original single 15-day plan (Render demo, Brevo, R2), replaced by the two phases |

## What changed on 2026-11-02

- The build is split into **Phase 1** (live in 11 days) and **Phase 2** (Jobs and Search, at the
  owner's pace).
- Email: **Resend** replaces Brevo (`deployment.md` §6).
- Media: **local storage** (a Docker volume served by Caddy); Cloudflare R2 moves to the backlog.
- Deployment: **straight to a VPS** at `distinctive.co.zw`, through a preview hostname; no Render
  demo.
- Conventions aligned with Consult 360: `CLAUDE.md`, `Development_Conventions.md`,
  `Phase_Gates.md`, commands files per day, the error log's templates and worked example,
  root-level `package.json` with `npm run build:css` and the `css-fresh` job, basedpyright,
  `makemigrations --check`, the 85% services coverage gate.
- `testing.md` became `Testing_Strategy.md` plus per-phase `Test_Plan.md` files;
  `task_breakdown.md` became the per-phase `Task_Breakdown.md` files.
