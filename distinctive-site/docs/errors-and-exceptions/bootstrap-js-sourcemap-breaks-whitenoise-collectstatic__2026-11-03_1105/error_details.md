# Prod `collectstatic` fails: Bootstrap's JS bundle references a missing `.map` file

- **Logged:** 2026-11-03 11:05 (first encountered)
- **Environment:** local (the prod `collectstatic` step the Dockerfile runs, run outside Docker)
- **Layer/Area:** Infra/Docker
- **Severity:** High (it would have failed every image build in CI's `build-and-push`)
- **Phase / day / card:** Phase 1 · Day 2 · WhiteNoise check

## What I was trying to do

Run the image build's static step locally after vendoring Bootstrap's JS bundle with
`npm run vendor`, as the Day 2 card says (`deployment.md` §2):

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod SECRET_KEY=build-only \
  DATABASE_URL=postgres://b:b@localhost/b python manage.py collectstatic --noinput
```

## Exact error / stack trace

```text
whitenoise.storage.MissingFileError: The file 'vendor/bootstrap/bootstrap.bundle.min.js.map'
could not be found with <whitenoise.storage.CompressedManifestStaticFilesStorage object …>.

The JS file 'vendor/bootstrap/bootstrap.bundle.min.js' references a file which could not be found:
  vendor/bootstrap/bootstrap.bundle.min.js.map
```

## Steps to reproduce

1. Copy `node_modules/bootstrap/dist/js/bootstrap.bundle.min.js` into `static/vendor/bootstrap/`
   as is, without its `.map`.
2. Run the prod `collectstatic` above.

## Initial suspected cause

The bundle's last line, `//# sourceMappingURL=bootstrap.bundle.min.js.map`. WhiteNoise's manifest
storage rewrites references in JS as well as CSS, and refuses one it can't resolve. This is the
same failure Consult 360 logged on 2026-10-05 for Chart.js
(`vendored-asset-trim-breaks-whitenoise-collectstatic`), with a different vendored file.
