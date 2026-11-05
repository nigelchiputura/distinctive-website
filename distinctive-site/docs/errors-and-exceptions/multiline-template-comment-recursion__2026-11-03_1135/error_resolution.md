# Resolution — Home returned 500: RecursionError while rendering the page

- **Resolved:** 2026-11-03 11:45
- **Time to resolve:** about 10 minutes

## Confirmed root cause

Django's `{# … #}` comment is **single-line only**. A `{#` with its `#}` on a later line isn't a
comment at all: the text is ordinary template content, and any tag inside it runs. `_image.html`
opened with a two-line usage note containing `{% include "includes/_image.html" … %}`, so the
template included itself, forever.

The same mistake was in four other new templates and in three from Days 3–4
(`templates/account/login.html`, `templates/allauth/layouts/base.html`,
`apps/core/templates/core/error.html`). Those three did no harm only by luck: they sit in child
templates outside any `{% block %}`, where Django ignores text.

## Fix applied (and why it works)

- Every multi-line comment is now `{% comment %} … {% endcomment %}`, which spans lines and
  whose contents are never parsed.
- `apps/pages/tests/test_home.py::test_no_multiline_hash_comments_in_templates` fails if any
  template has a `{#` whose `#}` isn't on the same line.

## Alternatives considered and rejected

- **Shorten every note to one line:** loses useful usage notes, and nothing stops the mistake
  coming back.
- **A lint tool for Django templates (djlint):** a new dependency and its own formatting rules, for
  one check that a ten-line test covers.

## Prevention (test / lint rule / doc)

- The test above runs in CI.
- `Development_Conventions.md` §7 and `CLAUDE.md` state the rule: `{# #}` for one line, `{% comment %}` for more.

## What this taught me about the stack

Django template comments don't behave like HTML or Jinja comments: `{# #}` can't span lines, and
when it fails it fails silently (the text prints) or, as here, by running whatever tags it holds.
Template-level mistakes rarely name the line at fault, so a failing page with an unexpected
recursion is worth checking for a broken comment first.
