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
| 1 | 5 | [Phase_1/day-5.md](./Phase_1/day-5.md) | Pages and Home: branch, unzip and `git rm` the placeholder, `up` and three migrations, CSS unchanged, Home empty before the seed, `seed_site_content` twice (adds, then nothing), Home at three widths, reorder a section and try the slider in the admin, the alt-text rule, the services list, the CI checks (167 tests), static step and `check --deploy`, PR |
| 1 | 6 | [Phase_1/day-6.md](./Phase_1/day-6.md) | About: branch, unzip and `git rm` the old home controller, `up` and two migrations, CSS unchanged, `seed_site_content` twice (team, partners, About's sections; then nothing), About at three widths, Read more with and without JavaScript, reorder the team and add a LinkedIn link in the admin, the CI checks (184 tests), static step and `check --deploy`, PR |
| 1 | 7 | [Phase_1/day-7.md](./Phase_1/day-7.md) | Nunito Sans and Services: branch, unzip and `git rm` Open Sans, `npm ci` + `vendor` + `build:css` (no change), three migrations, `seed_site_content` twice (adds Services and clients, fills Home's services; then nothing), the font on the site and admin, the Services page and its links, an enquiry through `ContactService` (console), Mark as handled and Resend in the admin, a real Resend send (owner), the CI checks (209 tests), static step and `check --deploy`, PR |
| 1 | 8 | [Phase_1/day-8.md](./Phase_1/day-8.md) | Contact and consent: branch, unzip, CSS unchanged, `up` (one migration; `createcachetable` in the entrypoint), `seed_site_content` twice (Contact's form and map, the Services enquiry block; then nothing), the Contact form with JavaScript on and off, the Services enquiry ("Services page" in the admin), the rate limit's sixth enquiry, cookie consent with placeholder values in the Network tab, the real Maps key and GA4 property (owner), the CI checks (249 tests), static step and `check --deploy`, PR |
| 1 | 9 | [Phase_1/day-9.md](./Phase_1/day-9.md) | Revised 2026-11-04: the team photo behind Home's hero, the gradient on the other heroes. UI and components polish (added 2026-11-04; the zip also carries Day 10's early SEO, redirect and production files): branch, unzip and `git rm` `read-more.js`, `npm ci` + `vendor` (17 icons) + `build:css` (no change), three migrations, `seed_site_content` twice (Contact's hero, the labels, the hero photo, nine redirects; then nothing), the new look on every page, the System / Light / Dark toggle with and without JavaScript, the bio dialog, back to top and reduced motion, Day 8's forms and consent re-checked, the CI checks (296 tests), static step and `check --deploy`, PR |
| 1 | 10 | [Phase_1/day-10.md](./Phase_1/day-10.md) | SEO, redirects, responsive images, production files and the demo: branch, unzip, CSS unchanged, no migrations, the search and sharing tags, `robots.txt` and the sitemap, old addresses (301, 302 for jobs, live pages untouched) and their hits, the branded 404, WebP copies on a phone, `check_redirects` on the old sitemap (owner), the CI checks (302 tests) and `check --deploy`, merge (builds the image), the optional local prod stack, and the demo on `new.distinctive.co.zw` (owner: server, GHCR login, `.env`, DNS, secrets, **Deploy VPS**) |
