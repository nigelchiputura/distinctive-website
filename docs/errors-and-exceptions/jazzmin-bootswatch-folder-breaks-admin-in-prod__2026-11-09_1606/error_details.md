# Every admin page answered 500 on the demo host: "Missing staticfiles manifest entry for 'vendor/bootswatch'"

- **Logged:** 2026-11-09 16:06 (first encountered)
- **Environment:** VPS preview (the Azure demo at `distinctive.garagegateexperts.online`)
- **Layer/Area:** Admin
- **Severity:** High (the public site worked, but nobody could use the admin on the demo host)
- **Phase / day / card:** Phase 1 · Day 10 · Demo on the preview host

## What I was trying to do

Signing in to the admin on the demo host for the first time, after `createsuperuser`. The sign-in
page loaded and accepted the password; the redirect to the admin's index page answered 500.

## Exact error / stack trace

```text
"POST /accounts/login/ HTTP/1.1" 302
"GET /admin-xxxxxxxx/ HTTP/1.1" 500 1336
ERROR django.request: Internal Server Error: /admin-xxxxxxxx/
Traceback (most recent call last):
  …
  File ".../django/templatetags/static.py", line 129, in handle_simple
    return staticfiles_storage.url(path)
  File ".../django/contrib/staticfiles/storage.py", line 204, in url
    return self._url(self.stored_name, name, force)
  File ".../django/contrib/staticfiles/storage.py", line 518, in stored_name
    raise ValueError(
ValueError: Missing staticfiles manifest entry for 'vendor/bootswatch'
```

## Steps to reproduce

1. Production settings (`config.settings.prod`, WhiteNoise's `CompressedManifestStaticFilesStorage`)
   and `collectstatic`, as the image does.
2. Sign in as a staff user.
3. Open any admin page: 500 with the error above.

## Initial suspected cause

A static file missing from the image: the vendored Bootstrap or one of Jazzmin's own files not
collected, like the Day 2 source-map lesson
(`bootstrap-js-sourcemap-breaks-whitenoise-collectstatic__2026-11-03_1105/`).
