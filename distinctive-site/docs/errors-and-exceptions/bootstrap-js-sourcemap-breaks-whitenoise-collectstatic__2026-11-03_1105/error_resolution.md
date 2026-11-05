# Resolution — Prod `collectstatic` fails: Bootstrap's JS bundle references a missing `.map` file

- **Resolved:** 2026-11-03 11:10
- **Time to resolve:** about 5 minutes (the Consult 360 entry pointed straight at it)

## Confirmed root cause

`CompressedManifestStaticFilesStorage` (prod only) post-processes JS as well as CSS. It treats the
trailing `//# sourceMappingURL=…` comment as a reference and raises `MissingFileError` because the
`.map` file wasn't vendored. Dev settings use plain static serving, so the page looked fine
locally; only the prod build step fails.

## Fix applied (and why it works)

`scripts/copy-vendor.mjs` now copies the bundle through `copyWithoutSourceMap`, which drops the
trailing source-map comment. With no reference left, WhiteNoise has nothing to resolve. The
re-vendored `static/vendor/bootstrap/bootstrap.bundle.min.js` is committed. Re-run with
`npm run vendor`; the Day 2 commands file includes the check.

## Alternatives considered and rejected

- **Vendor the `.map` too:** it ships a 300 KB file nobody uses in production.
- **Set `WHITENOISE_MANIFEST_STRICT = False`:** that hides every missing reference, including
  real broken font or image URLs in our own CSS, which is exactly what this check is for.
- **Load Bootstrap from a CDN:** a third-party request before consent, and against the
  self-hosted decision in `frontend.md`.

## Prevention (test / lint rule / check / doc)

- The fix lives in the vendoring script, so re-vendoring after a version bump can't bring the
  line back.
- `frontend.md` §1 already says: after changing a vendored package, run `npm run vendor` and the
  prod `collectstatic`. The Day 2 commands file runs it.
- The Dockerfile runs the same step, so CI's image build would fail loudly rather than ship.

## What this taught me about the stack

WhiteNoise's manifest storage checks **every** `url()` in CSS and every `sourceMappingURL` in JS
at build time. Vendored files from npm usually end with a source-map comment, so any vendored JS
or CSS needs the comment removed or its map copied too. The same lesson as Consult 360's, with a
different file: worth checking first whenever `collectstatic` fails in prod only.
