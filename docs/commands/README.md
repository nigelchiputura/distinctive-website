# Commands — what to run after each day

**Commands are written for a Linux shell (bash). On Windows or macOS, read
[Terminal_Note.md](./Terminal_Note.md) first.**

One Markdown file per completed day. Each one lists the terminal commands to run after that
day's code is in place, and what each step should print. Files are grouped by phase:

```
commands/
├── README.md            # this file
├── Terminal_Note.md     # commands are bash; Windows/macOS equivalents
├── Phase_1/
│   ├── day-1.md         # added when Day 1 is completed
│   └── …
└── Phase_2/             # created on the first day of Phase 2
    └── day-1.md         # Phase 2 restarts its day numbering at 1
```

## Rules for these files

- **Written on the day it is completed**, in the same piece of work as the code
  (`../../CLAUDE.md` rule 4, `../Development_Conventions.md` §3.2). If a fix changes the commands
  later, the file is edited in place and its "Revised" line is updated.
- **Run from the repo root, in bash.** Where a common step differs on Windows, a labelled
  `PowerShell:` form is given too; otherwise see `Terminal_Note.md`.
- **Each step says what to expect.** Without that, a person can't tell a pass from a quiet
  failure.
- **ONE-TIME steps are marked**, so re-running a day doesn't repeat destructive steps like
  `down -v`.
- **Complete, not incremental.** Each file lists everything needed to bring that day's work up
  and check it, including migrations, `npm run build:css`, seeding and tests. It does not
  depend on reading the earlier files.
- **Markdown** (`day-M.md`): a header block (**Cards**, **Completed**, **Revised**), one `##`
  heading per numbered step, commands in fenced code blocks labelled `bash` or `powershell`,
  and a bold **Expect:** line after them.
- Folders are named `Phase_N` to match `docs/Phase_N/` (no spaces in paths).

## Index

| Phase | Day | File | Summary |
|---|---|---|---|
| 1 | 1 | [Phase_1/day-1.md](./Phase_1/day-1.md) | Revised 2026-11-03: `SECRET_KEY` 50+ characters; `createsuperuser` asks only for an email. Skeleton: create the repo and push, `.env`, `up --build`, health check, migration order (users before admin), superuser, data survives `down`/`up`, the CI checks in the container, `check --deploy`, the stale-image guard, branch protection |
| 1 | 2 | [Phase_1/day-2.md](./Phase_1/day-2.md) | Sass pipeline and layout: branch, unzip over the repo, `SECRET_KEY` length, Node 22, `npm ci` + `build:css` (no change), `npm run vendor` (no change), the layout at 1280/768/375 px, prod `collectstatic` + `check --deploy`, the CI checks (28 tests), PR with both checks green, optional proof that `css-fresh` fails on stale CSS |
| 1 | 3 | [Phase_1/day-3.md](./Phase_1/day-3.md) | Base classes and site settings: branch, unzip, `up --build` (new packages; three migrations), CSS unchanged, the client's logo, editing Site settings in the admin (a social icon appears), `createsuperuser` asks only for an email, the `core.W001`/`W002` checks and a mistyped `EMAIL_PROVIDER`, the CI checks (101 tests), `check --deploy`, PR |
| 1 | 4 | [Phase_1/day-4.md](./Phase_1/day-4.md) | Sign-in and onboarding: branch, unzip, `up --build` (allauth, Jazzmin; new migrations), CSS unchanged (now two files), the staff sign-in page and the Jazzmin admin, sign-up closed, add a user in the admin and follow the emailed link, the editor sees only Site settings, `onboard_user`, Google sign-in setup (owner), the CI checks (134 tests), static step and `check --deploy`, PR |
