# Resolution — The sign-in pages lost the top bar's and footer's details

- **Resolved:** 2026-11-03 11:30
- **Time to resolve:** about 10 minutes

## Confirmed root cause

A context-variable name collision. allauth's views put the `django.contrib.sites` record into
their template context as **`site`**. View context wins over context processors, so on those pages
`site` was the `Site` object (`domain`, `name`), not our `SiteDetails`. `{{ site.phone_display }}`
on a `Site` is an empty string, so the labels and links vanished with no error. The sign-up-closed
page rendered correctly because that view doesn't add `site`, which is what pointed away from the
CSS.

## Fix applied (and why it works)

- The context processor now returns **`site_info`** (`apps/core/context_processors.py`, with a
  comment saying why), and every template uses `site_info.…`: `base.html`, `_topbar.html`,
  `_navbar.html`, `_footer.html`, the allauth layout, and the core error and placeholder pages.
  No library uses `site_info`.
- `apps/users/tests/test_sign_in.py::test_sign_in_page_is_staff_only_with_no_sign_up_link`
  asserts the phone number appears on `/accounts/login/`.

## Alternatives considered and rejected

- **Remove `site` from allauth's context:** it means overriding allauth's views, and the Sites
  framework's `site` is a common name other packages also use.
- **Keep `site` and also set `SITE_ID` details:** the `Site` object can't carry our fields.

## Prevention (test / lint rule / doc)

- The sign-in test above, plus `test_layout.py`, check the details render.
- `architecture.md` §4 notes the name and the reason.
- Day screenshots of every new page type stay part of each day's check: this bug produced no
  error and no failing test until the test was written.

## What this taught me about the stack

Template context is one flat namespace shared by context processors, the view and every
third-party app's views, and the view silently wins. Generic names (`site`, `user`, `form`,
`request`, `messages`, `view`) are taken or likely to be. Give project-wide context variables a
name no library would choose.
