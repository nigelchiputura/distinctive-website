# Errors & Exceptions — Index

Chronological log of every non-trivial error hit during this build, most recent first. See
`../Errors_And_Exceptions.md` for the full process, the tags, and the "when to log this"
guideline.

**Add a row here at the same time you write an entry's two files.** This table is what makes the
log browsable, since the folder names sort by error name, not by date.

| Date | Error | Layer/Area | Severity | Folder |
|---|---|---|---|---|
| 2026-11-03 11:05 | Prod `collectstatic` failed: Bootstrap's vendored JS bundle referenced a missing `.map` file (the Consult 360 Chart.js lesson, again) | Infra/Docker | High (caught before shipping) | [bootstrap-js-sourcemap-breaks-whitenoise-collectstatic__2026-11-03_1105](./bootstrap-js-sourcemap-breaks-whitenoise-collectstatic__2026-11-03_1105/) |

## How to add an entry

1. Copy `_templates/error_details_TEMPLATE.md` and `_templates/error_resolution_TEMPLATE.md`
   into a new folder named `<error-slug>__<YYYY-MM-DD_HHMM>/` (timestamp = when you first hit
   the error, not when you fixed it), renaming them `error_details.md` and
   `error_resolution.md`.
2. Fill in `error_details.md` while still investigating, if possible (see
   `../Errors_And_Exceptions.md` §3 for why that timing matters).
3. Fill in `error_resolution.md` once it is actually fixed.
4. Add a row to the table above (replace the placeholder row with the first real entry).
5. If the fix touched shared code, link this folder from the relevant GitHub Issue or task card
   rather than re-explaining it there.

See `_example-entry__2026-01-01_0000/` for a fully worked example of both files.
