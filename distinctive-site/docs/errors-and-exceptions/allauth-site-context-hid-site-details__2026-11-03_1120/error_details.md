# The sign-in pages lost the top bar's phone, email and social links, and the footer's details

- **Logged:** 2026-11-03 11:20 (first encountered)
- **Environment:** local (runserver, checked with Playwright screenshots)
- **Layer/Area:** View
- **Severity:** Medium (no error anywhere; only visible by looking at the page)
- **Phase / day / card:** Phase 1 · Day 4 · allauth

## What I was trying to do

Check the new allauth pages (sign in, set password) at 1280 px after wrapping them in the site's
own layout (`templates/allauth/layouts/base.html` extends `base.html`).

## Exact error / stack trace

No error, no warning, status 200. On `/accounts/login/` and the set-password page the top bar
showed only the phone and envelope **icons**: no number, no address, no social icons. The footer's
"Reach Us" values were blank too. `/accounts/signup/` (also an allauth page) looked right, as did
every non-allauth page.

## Steps to reproduce

1. Have the context processor `apps.core.context_processors.site` return `{"site": SiteDetails}`.
2. Render any template that uses `{{ site.phone_display }}` from allauth's login view.

## Initial suspected cause

The CSS: `_auth.scss` uses `@extend .form-control` and `@extend .btn`, and I suspected an
`@extend` had pulled the top bar's labels into a hidden state, the way `.topbar__label` is
visually hidden on phones.
