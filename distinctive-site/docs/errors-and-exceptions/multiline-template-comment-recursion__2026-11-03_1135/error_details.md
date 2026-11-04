# Home returned 500: RecursionError while rendering the page

- **Logged:** 2026-11-03 11:35 (first encountered)
- **Environment:** local (runserver)
- **Layer/Area:** View
- **Severity:** High (the home page didn't render; caught before shipping)
- **Phase / day / card:** Phase 1 · Day 5 · Templates

## What I was trying to do

Load `/` for the first time after adding `pages/home.html` and the new includes
`_hero_slider.html`, `_section.html`, `_service_card.html` and `_image.html`.

## Exact error / stack trace

```
RecursionError: maximum recursion depth exceeded
  File ".../django/template/loader_tags.py", line 205, in render
    name: var.resolve(context) for name, var in self.extra_context.items()
  …
ERROR django.server: "GET / HTTP/1.1" 500 4975021
```

The traceback repeated `loader_tags.py` (the `{% include %}` node) thousands of times. No line in
our templates was named.

## Steps to reproduce

1. In `templates/includes/_image.html`, start with a usage note in a `{# … #}` comment that spans
   two lines and contains `{% include "includes/_image.html" with obj=section %}`.
2. Include `_image.html` from any page and render it.

## Initial suspected cause

A context variable resolving to itself: `{% with s=section %}` in `_section.html`, or the page's
`content` variable sharing its name with the `{% block content %}`.
