# Every page scrolled sideways on phones: `row g-5` was 12 px wider than the screen

- **Logged:** 2026-11-04 19:50 (first encountered)
- **Environment:** local (dev server, headless Chromium at 390 px)
- **Layer/Area:** Frontend/SCSS
- **Severity:** Medium (caught before shipping, but every page on every phone was affected)
- **Phase / day / card:** Phase 1 · Day 9 · Modern components

## What I was trying to do

Taking screenshots of the redesign for the stakeholder email. The phone screenshots
(`device_scale_factor=2`, 390 px wide) came out 804 px wide instead of 780, with a grey strip
down the right-hand side.

## Exact error / stack trace

```text
No error. Measured in the browser at 390 px:
/          scrollWidth 402, clientWidth 390
  div.row.g-5.align-items-center right=402
  div.col-lg-6.value-block__media right=402
  …
  div.row.g-5 right=402            (the footer)
/about/    scrollWidth 402 …
/services/ scrollWidth 402 …
/contact/  scrollWidth 402 …
```

## Steps to reproduce

1. Open any page at 390 px wide.
2. Drag the page sideways: it moves about 12 px and shows a strip on the right.
3. In DevTools, list elements whose right edge is beyond the window: every `.row.g-5`.

## Initial suspected cause

Something new on Day 9 that is wider than the screen, perhaps the framed images' offset outline
or the cookie card.
