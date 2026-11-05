# Resolution — Every page scrolled sideways on phones: `row g-5` was 12 px wider than the screen

- **Resolved:** 2026-11-04 20:00
- **Time to resolve:** 10 minutes

## Confirmed root cause

Bootstrap's gutter classes give a row negative side margins of half the gutter. `g-5` is a 3 rem
gutter, so the row reaches 1.5 rem beyond its container on each side. The container's own padding
is only 0.75 rem below 992 px, so each `g-5` row stuck out 0.75 rem (12 px) past the screen.
Inside bands this was clipped (`.band` has `overflow: hidden`), but the footer has no band
around it, so the footer's row widened the whole page on every page.

## Fix applied (and why it works)

Every `class="row g-5"` in `templates/` is now `class="row g-4 g-lg-5"`: a 1.5 rem gutter (0.75 rem
of negative margin, exactly the container's padding) below 992 px, and the wider gutter only
where the container has room for it. Files: `templates/includes/_section.html`,
`_service_bands.html`, `_footer.html`. `commands/Phase_1/day-9.md` was revised: step 5 now checks
for sideways scroll at 375 px.

## Alternatives considered and rejected

- `overflow-x: hidden` on `body`: hides the symptom, breaks `position: sticky` on the navbar in
  some browsers, and would hide the next overflow too.
- Bigger container padding on phones: wastes width on the smallest screens.

## Prevention (test / lint rule / check / doc)

- `apps/core/tests/test_polish.py::test_no_bare_g5_gutters` fails if a template uses `row g-5`
  without a smaller gutter for phones.
- `frontend.md` §8 states the rule (`g-4 g-lg-5`, never a bare `g-5`).
- The Phase 1 manual QA already checks every page at 375 px for sideways scroll; the browser
  check (`scrollWidth == clientWidth` on all four pages) is now part of each day's screenshots.

## What this taught me about the stack

Bootstrap's large gutters assume the large container padding. A full-page screenshot that comes
out wider than the viewport is a quick tell for horizontal overflow.
