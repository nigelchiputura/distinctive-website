# Phase Gates

How the project moves from one phase to the next. A phase is **complete** only when every item
on its completion checklist is true, and the completion is **affirmed in writing** before any
work on the next phase starts.

## 1. Phases at a glance

| Phase | Purpose | Status (2026-11-04) | Docs |
|---|---|---|---|
| **Phase 1** | Something visual, live: Home, About, Services and Contact, all admin-editable, replacing the WordPress site on `distinctive.co.zw` | **In progress.** Days 1–9 of 11 completed 2026-11-03/04 (Day 9, UI and components polish, added 2026-11-04) | `Phase_1/` |
| **Phase 2** | Jobs (list, detail, Markdown postings) and site-wide Search (dropdown, results, highlighting) | **Draft.** Built at the owner's pace after the Phase 1 gate; no fixed deadline | `Phase_2/` |
| **Backlog** | Optional improvements, built when the client needs them | Listed only | `Phase_2/Phase2_Scope.md` §6 |

Update the Status column at each gate.

## 2. The gate rule

1. When the last card of a phase's `Task_Breakdown.md` is done, the phase's **completion
   checklist** (§3) is worked through item by item, with evidence for each (CI run link, live
   URL, QA checklist ticked, sign-off note).
2. The result is stated plainly in one of two forms:
   - **"Phase N build complete."** followed by the evidence, item by item; or
   - **"Phase N not complete."** followed by exactly what is outstanding.
3. Only after "complete" is affirmed does the next phase's **kickoff** begin (§4). No next-phase
   code is written before that, even if a next-phase task looks quick.
4. The gate is affirmed by whoever is driving the build (the developer, or Claude when Claude is
   building) and agreed by the project owner.

## 3. Completion checklist (applies to every phase)

- [ ] Every card in `Phase_N/Task_Breakdown.md` is Done (or explicitly moved to a later phase,
      with the reason written on the card).
- [ ] Every completed day has its commands file in `commands/Phase_N/`, indexed in
      `commands/README.md` (`Development_Conventions.md` §3.2).
- [ ] CI is green on `main`: `ruff`, `basedpyright`, `makemigrations --check`, `pytest` with
      coverage ≥ 85% on services, `css-fresh`.
- [ ] Every required test in `Phase_N/Test_Plan.md` §3 exists and passes.
- [ ] The manual QA checklist in `Phase_N/Test_Plan.md` §4 is fully ticked.
- [ ] The phase is deployed to production (`distinctive.co.zw`) and the client walkthrough is
      done.
- [ ] Every non-trivial error hit during the phase is logged in `errors-and-exceptions/`.
- [ ] The living docs describe the system **as built**: `architecture.md`, `folder_structure.md`,
      `frontend.md`, `deployment.md`, `users.md`.
- [ ] Open client questions for the phase are answered, or carried into the next phase's scope.
- [ ] The project owner has signed off the phase.

## 4. Kickoff of the next phase

1. Re-read the next phase's draft docs against what the finished phase taught us and the
   client's latest answers. Update them.
2. Settle the next phase's open questions (`Phase_N/PhaseN_Scope.md` §5).
3. Change each next-phase doc's status line from **Draft** to **Agreed (date)**.
4. Set up the task board for the new `Task_Breakdown.md`.

## 5. Where documents live

| Kind of document | Location | Example |
|---|---|---|
| **Project-wide** (true for the whole project, kept current) | `docs/` | `Development_Conventions.md`, `architecture.md`, `frontend.md`, `deployment.md`, `users.md`, `Testing_Strategy.md`, `Errors_And_Exceptions.md`, `Phase_Gates.md` |
| **Phase-scoped** (only about one phase) | `docs/Phase_N/` | `Phase_1/Phase1_Scope.md`, `Phase_1/Task_Breakdown.md`, `Phase_1/Test_Plan.md` |
| **Designs not yet built** | `docs/Phase_N/` until built | Jobs and Search designs in `Phase_2/Phase2_Scope.md` |
| **Commands per day** | `docs/commands/Phase_N/` | `commands/Phase_1/day-1.md` |
| **Error log** | `docs/errors-and-exceptions/` | `errors-and-exceptions/README.md` |
| **Superseded** | `docs/archive/` | `archive/task_breakdown__15-day-plan__superseded_2026-11-02.md` |

When a phase's features are built, their designs are written into the living docs
(`architecture.md`, `frontend.md`). Scope, task and test documents stay in `docs/Phase_N/` as
the record of that phase.

**References** between documents are written relative to `docs/`, for example
`Phase_1/Phase1_Scope.md` or `architecture.md`.
