# Resolution — Every admin page answered 500 on the demo host: "Missing staticfiles manifest entry for 'vendor/bootswatch'"

- **Resolved:** 2026-11-09 16:40 (in the code; live once the image is rebuilt and deployed)
- **Time to resolve:** about 35 minutes

## Confirmed root cause

Nothing was missing from the image. Jazzmin 3.0.5's `admin/base.html` has
`data-theme-base="{% static 'vendor/bootswatch' %}"` on its theme stylesheet link: the URL of a
**folder**, which its theme chooser uses as a base. WhiteNoise's manifest storage only knows
files, and in strict mode (the default) it raises for any name not in its manifest, so every
admin page failed to render. The public pages never ask for that folder, so they worked.

It got this far because nothing before production used the manifest storage while rendering the
admin: tests and the dev server use Django's plain storage, which never checks that a file
exists; Day 10's gunicorn check with prod settings and Lighthouse only opened the public pages.

## Fix applied (and why it works)

`apps/core/storage.py`: `StaticStorage`, WhiteNoise's `CompressedManifestStaticFilesStorage` with
a named set of folders (`UNHASHED_FOLDERS = {"vendor/bootswatch"}`) whose URL is returned as it is.
`config/settings/prod.py` uses it for `staticfiles`. Every other name missing from the manifest
still raises, so a real missing file is still caught. The folder's URL is only a base for theme
addresses (and we use the default theme), so nothing is ever fetched from it.

## Alternatives considered and rejected

- `manifest_strict = False` for the whole storage: fixes this, and silently serves an unhashed
  (probably 404) URL for every real typo or missing file, which is exactly what the strict
  manifest is there to catch.
- Overriding Jazzmin's `admin/base.html`: a large template to copy and keep in step with each
  Jazzmin release, to change one attribute.
- Pinning an older Jazzmin: the attribute is in the current release; no fix upstream to move to.

## Prevention (test / lint rule / check / doc)

- `apps/core/tests/test_static_storage.py`: runs `collectstatic` into a scratch folder with the
  production storage and opens the admin as a superuser (it failed with this error before the fix);
  plus unit tests that the folder passes, a real file is hashed, and any other missing name still
  raises.
- The Phase 1 manual QA now opens the admin on the local prod stack and the preview host, not only
  the public pages (`Phase_1/Test_Plan.md` §4).

## What this taught me about the stack

A check with production settings is only as good as the pages it opens. The manifest storage
fails at render time, per template, so the admin (a third-party template) needs its own look.
