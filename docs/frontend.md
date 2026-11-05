# Frontend

**Project-wide · revised 2026-11-04** (Day 7 as built: the Services page; the font is Nunito Sans;
Day 6: About, the team and logo blocks, Read more; Day 5: Home, the section partial, the hero slider and its JS; Day 2: sampled brand colours, inline SVG icons, Node 22; 2026-11-02: npm and SCSS at
the repo root as in Consult 360, Phase 1 pages, Jobs and Search designs moved to `Phase_2/Phase2_Scope.md`)

Django templates (SSR) + Bootstrap 5 (customised) + vanilla JS ES modules + CSS compiled from
Sass. AJAX only where it helps: the contact and enquiry forms (Phase 1), the search dropdown
(Phase 2).

## 1. Stack and build

| Concern | Choice |
|---|---|
| Markup | Django templates, partials in `templates/includes/` |
| Components | Bootstrap 5 from npm, its Sass variables overridden before import |
| Styles | SCSS in `static/scss/`, compiled with **Dart Sass** (the `sass` npm package) |
| Behaviour | Vanilla JS ES modules in `static/js/`, no bundler |
| Vendor assets | Bootstrap's JS bundle (`static/vendor/bootstrap/`, source-map line removed) and Nunito Sans `woff2` (`static/vendor/nunito-sans/`), copied from `node_modules` by `npm run vendor` and committed |
| Icons | Font Awesome Free SVGs, written by `npm run vendor` as inline partials in `templates/includes/icons/` (`{% include "includes/icons/phone.svg" %}`). No icon webfont to download; each icon takes the text colour |
| Fonts | **Nunito Sans** (the owner's choice, 2026-11-04; the old site used Open Sans), self-hosted, on the site and in the admin |

### Node on the dev machine only

```jsonc
// package.json (repo root)
{
  "private": true,
  "scripts": {
    "build:css": "sass static/scss/main.scss:static/css/main.css static/scss/admin.scss:static/css/admin.css --style=compressed --no-source-map --load-path=node_modules --quiet-deps --silence-deprecation=import",
    "watch:css": "sass static/scss/main.scss:static/css/main.css static/scss/admin.scss:static/css/admin.css --watch --no-source-map --load-path=node_modules --quiet-deps --silence-deprecation=import",
    "vendor": "node scripts/copy-vendor.mjs"
  },
  "engines": { "node": ">=22" },
  "devDependencies": {
    "@fontsource/nunito-sans": "5.3.0",
    "@fortawesome/fontawesome-free": "7.3.1",
    "bootstrap": "5.3.8",
    "sass": "1.107.1"
  }
}
```

- Node 22 or later (Node 20 reached end of life in April 2026). Node and npm exist only on the
  developer machine and in CI's `css-fresh` job. **Neither is in any image or on any server.**
- Versions are pinned exactly (`npm install --save-dev --save-exact`), so CI compiles
  byte-identical CSS.
- Two stylesheets: `static/css/main.css` (the site) and `static/css/admin.css` (a few rules for
  the Jazzmin admin, from `static/scss/admin.scss`, using the same tokens). Both are committed. CI
  rebuilds them and fails on any difference in `static/css/`, or if a `sourceMappingURL` slipped
  in (`deployment.md` §5).
- Run `npm run build:css` before committing any SCSS change.
- After changing a vendored package, run `npm run vendor` and the local prod `collectstatic`
  (`deployment.md` §2): WhiteNoise rejects CSS or JS that references a missing file, including
  a vendored bundle's `sourceMappingURL` line (`copy-vendor.mjs` strips it; see
  `errors-and-exceptions/bootstrap-js-sourcemap-breaks-whitenoise-collectstatic__2026-11-03_1105/`).
- The full Bootstrap build is about 237 KB minified, 33 KB gzipped. If Lighthouse asks for less on
  Day 9, import only the Bootstrap partials in use.

## 2. SCSS architecture

`main.scss` order matters:

```scss
@import "tokens";                            // 1. $dcs-* brand tokens
@import "variables";                         // 2. Bootstrap variable overrides (use the tokens)
@import "bootstrap/scss/bootstrap";          // 3. Bootstrap, themed by 1–2
@import "fonts";                             // 4. our rules
@import "base";
@import "components/topbar";
@import "components/navbar";
@import "components/footer";
@import "components/auth";                   // Day 4: the sign-in pages
@import "components/buttons";                // Day 5: .btn-outline-gold, .btn-outline-gold-dark
@import "components/hero";                   // Day 5: the slider and the hero_text band
@import "components/section";                // Day 5: bands, CTA, value blocks
@import "components/cards";                  // Day 5: service cards
@import "components/logos";                  // Day 6: partner and client logos
@import "components/team";                   // Day 6: Our Leadership, Read more
@import "components/services";               // Day 7: the Services page
// Day 8: components/forms, components/cookie-banner.
// pages/about, pages/services, pages/contact only if a page needs rules of its own.
```

`@import` is fine for now: `--silence-deprecation=import` quiets Dart Sass's warning about our own
`@import`s, and `--quiet-deps` hides Bootstrap's. The build prints no warnings; keep it that way
(no `darken()`/`lighten()`: add a token instead). Migrate to `@use` when Bootstrap's Sass supports
it cleanly. Partials are added to `main.scss` on the day their component arrives.

**Colours only through tokens.** SCSS uses `$dcs-*`; `_tokens.scss` also emits them as `--dcs-*`
custom properties on `:root` for the few places JS or inline styles need them. No raw hex values
outside `_tokens.scss`.

### Brand tokens (sampled from the old site's screenshots on 2026-11-03; confirm against the logo file, Phase 1 Q5)

| Token | Value | Use | Contrast |
|---|---|---|---|
| `$dcs-black` | `#000` | Top bar, footer, dark bands | — |
| `$dcs-black-soft` | `#0d0d0d` | Footer navigation strip | — |
| `$dcs-charcoal` | `#242424` | Home services band, capability band | — |
| `$dcs-charcoal-light` | `#333` | The mat around service-card images | — |
| `$dcs-grey` | `#666` | Navbar links, muted text on white | 5.7:1 on white |
| `$dcs-grey-on-dark` | `#a6a6a6` | Copyright line on black (the old `#666` was 3.7:1) | 8.6:1 on black |
| `$dcs-text` | `#222` | Body text | — |
| `$dcs-gold` | `#d4af37` (exactly the old theme's) | Headings and links on dark, active-nav underline, CTA outline | 10:1 on black, **2.1:1 on white** |
| `$dcs-gold-dark` | `#86691a` | Gold **text** on light backgrounds (links, active nav) | 5.2:1 on white |
| `$dcs-gold-deeper` | `#6b5415` | Hover on `$dcs-gold-dark` links | — |
| `$dcs-white` | `#fff` | Light bands, navbar | — |
| `$dcs-navy` → `$dcs-blue` | `#02070b` → `#1f5fa8` | About "Our Story" gradient (sampled on Day 6). The old band ran on to `#2a85d6`; it stops darker here | white text 6.4:1 or better throughout (the old end was 3.9:1) |
| `$dcs-font-sans` | Nunito Sans 400/600/700, then system fonts | All text, site and admin (`admin.scss` imports `_fonts.scss` too) | — |

**The logo** is the file the client sent on 2026-11-03: `static/img/logo.png`, a transparent PNG
trimmed to 172 × 100 and reduced to 128 colours (3.9 KB). It shows at 60 px high, so on high-density
screens it is slightly soft; an SVG (or a PNG at least 2× the size) would make it crisp. Its gold
is a gradient around `#d2a22f`, close to the site's `#d4af37`, which stays as the old theme's.

Bootstrap overrides: `$primary: $dcs-gold`, `$body-color`, `$font-family-sans-serif`,
`$link-color: $dcs-gold-dark`, `$navbar-light-*`, `$btn-border-radius`, `$headings-color`.

## 3. Templates

```
base.html
 ├─ includes/_seo.html            <title>, meta description, canonical, OG/Twitter, JSON-LD (Day 9)
 ├─ includes/_topbar.html         phones, email, social icons (site_info)
 ├─ includes/_navbar.html         logo + nav items from the context processor
 ├─ <main id="main"> {% block main %}{% block content %}   pages fill "content";
 │                                 a layout can wrap it by overriding "main"
 ├─ includes/_footer.html         "Reach Us", footer nav, copyright, "Cookie settings" link
 ├─ includes/_cookie_banner.html  (Day 8)
 └─ Bootstrap's bundle (defer), then js/main.js (type="module")

pages/page.html                   any page: a visually hidden h1 unless the first section is a hero_text band,
                                  then includes/_section.html per section
pages/home.html                   extends page.html; its top is includes/_hero_slider.html
includes/_section.html            one PageSection, by section_type (table below)
includes/_service_card.html       one offerings.Service on Home
includes/_logo_grid.html          partner or client logos (pages.Partner)
includes/_team_card.html          one team.TeamMember
includes/_image.html              an admin image with its stored width/height and alt text
```

The site's details are `site_info` in every template (not `site`: allauth's views use that name).
`templates/allauth/layouts/base.html` overrides `main` to put every allauth page (sign in,
set password, sign out …) in a card on a light grey band; `templates/account/` holds our own
sign-in and set-password pages (`users.md` §3).

**Template comments:** `{# … #}` must open and close on one line; anything longer is
`{% comment %} … {% endcomment %}` (`Development_Conventions.md` §7; a test enforces it).

**Images from the admin** go through `includes/_image.html`. `ImageMixin` (`apps/core/models.py`)
stores each upload's width and height, so `<img>` always has them and the page doesn't jump while
images load; alt text is required unless the editor ticks "decorative image" (then `alt=""`).
Images are `loading="lazy"` except the first hero slide, which gets `fetchpriority="high"`.

`includes/_section.html` renders a `PageSection` by `section_type`, with `id="{{ section.anchor }}"`:

| `section_type` | Look (from the old site) |
|---|---|
| `hero_text` | Full-width image band with a large heading; the page's `h1` when it's the first section |
| `intro_dark` | Black band, gold heading, white text ("What We Do") |
| `band_light` / `band_dark` | Alternating bands used on Services; heading left- or right-aligned |
| `two_column` | "Our Story": a navy-to-blue band; heading and the section's **short text** (`intro`) left, the body right |
| `value_block` | Image one side (the section's "image position"), heading and paragraph the other; image first on phones. Consecutive value blocks share one white band |
| `service_bands` | The Services page: a row of links to every service, then each published service in its own band, alternating black (heading on the right on wide screens) and white, with `id="<anchor>"`. A service's image shows beside its text only when "show the image on the Services page" is ticked (the NGO diagram); the Home card images don't. Long lists go into two columns on wide screens |
| `service_cards` | Charcoal band with the services ticked "show on Home" (at most six), as framed cards linking to `/services/#<anchor>`. Card titles are `h2` when the section has no heading, `h3` under one |
| `partners` / `clients` | White band with the published logos of that kind, centred, each scaled into the same 8 rem box without cropping, caption below, linked when it has a website |
| `team` | White band, uppercase dark-gold heading, the published team: four across on wide screens, two on tablets, one on phones; round photos, name, job title in grey, bio, LinkedIn and Facebook icons when filled in |
| `cta` | A centred line and an outlined gold button ("Get In Touch") |

The editor picks the look per section and orders sections freely, so each page's order is data,
not template code. Every section also has a **heading position** (left, centre, right; right
falls back to left below 992 px). The blocks that show other content (`service_cards`,
`partners`, `clients`, `team`) can go on any page: `PageBlocksService` fetches each one only
when a section uses it (`architecture.md` §5).

Markdown bodies go through `{{ section.body|markdown }}` (load `core_extras`). Nothing else turns admin text into HTML.

## 4. Page notes (from the reference screenshots)

### Global

- **Top bar (black):** phone `+263 (24) 2 486 642 - 3`, `enquiries@distinctive.co.zw`, social
  icons (Facebook, LinkedIn, Instagram, X), each a `SiteSettings` URL and shown only if filled
  in. RSS dropped. Below 576 px the phone number and email show as icons only (still links,
  with screen-reader labels), so the bar stays one line.
- **Navbar (white, sticky):** logo left; **Phase 1:** Home, About Us, Services, Contact Us, from
  `NavigationService`. Phase 2 adds Jobs and the search icon. Dark gold marks hover and the
  current page, which also gets a gold underline and `aria-current="page"` (colour alone isn't
  enough). Below 992 px the links collapse behind the toggler.
- **Footer:** black "Reach Us" block (blurb; 62 Mutare Road, Beverly, Msasa, Harare; phone;
  hours 8:00am–4:30pm Mon–Fri; email); a strip with the footer nav; a bottom line with copyright,
  social icons and "Cookie settings". All values from `SiteSettings`.
- **Not carried over:** the WordPress "Categories" footer widget, the RSS icon, the old sidebar
  search box, and the "Designed by" credit unless the client wants it (Phase 1 Q7).

### Home

1. Hero slider (`HeroSlide`): the first slide's heading is the page's `h1` ("Distinctive
   Consultancy Services", "Bringing excellence into your world."). The old site had three slides
   over a team photo; the seed has one slide and no photo (the old screenshots have the text
   printed over the photo), so it shows on a black-and-gold background until the original photo
   is uploaded. With no slides at all, a visually hidden `h1` keeps the page's outline.
2. Charcoal band with six service cards (a `service_cards` section): Industrial / Employee
   Relations, HR Audits, Talent Acquisition, People Strategy, Research Surveys, Organisational
   Design. Framed image, gold title, short blurb; each links to `/services/#<anchor>`. Card images
   are fitted inside a fixed 3:2 frame without cropping (`object-fit: contain`), because several
   have words in them.
3. CTA: "Get the best specialised business consultancy services in Africa." + outlined gold
   "Get In Touch" → `/contact/`.
4. Two value blocks on white: **People Centred** and **Proactive**, image alternating.

### About

As built on Day 6, all from sections in the admin:

1. `hero_text`: "Bringing Excellence Into Your World!" (the page's `h1`). The old compass photo had
   the heading printed over it, so it shows on the plain black-and-gold background until the
   original is uploaded.
2. `two_column` **Our Story**: the gradient band, short text left, long text right with bold key
   phrases.
3. `partners` **Strategic Partners**: Emergence Growth and Bindura University of Science
   Education.
4. `band_dark` **Capability Analysis**: the old run-on dashes are now a list, with the image
   beside the text; `band_dark` **Value Driven and Capacity Building** with its heading on the
   right.
5. `team` **Our Leadership**: eight people. Bios are left-aligned (the old ones were justified,
   with gaps). A bio longer than about nine lines is cut behind **Read more** on every screen size,
   so the cards line up; without JavaScript every bio shows in full.

### Services

As built on Day 7, all from sections in the admin:

1. `hero_text` **Our Services** (the `h1`) with the old "What We Do" paragraph under it. The old
   page's 13-slide slider is gone: it repeated the service names, which the links below now do.
2. `service_bands` **What We Do**: links to all 13 services, then their bands. The old page's
   wording is kept, tidied ("Organizational" → "Organisational", run-on lists as lists).
   "Rightsizing / Organisational Design" is the service called **Organisational Design** (one name
   for its Home card and its band). The NGO Capacity Development diagram also appears as text, so
   its content isn't only in an image. The order groups related services, starting with the
   ones on Home; editors change it in the Services list.
3. `clients` **Some of Our Corporate Clients**: ten logos, five to a row on wide screens.
4. Day 8 adds the gold "Get In Touch With Us" block: a general enquiry form (first name, last name,
   email, message) posting to the contact service with `source_page=services`; button "Send
   enquiry".

### Contact

- Black band: "Get In Touch!" form (Name, Email Address, Message, Submit) left; "Reach Us" right,
  including the vacancies line until Phase 2 ("Send your CV to recruitment@…", from
  `SiteSettings.recruitment_email`).
- Map band: an interactive Google Map (Maps Embed API iframe, key restricted by HTTP referrer),
  injected **only after cookie consent**. Before consent: the address and a "Get directions"
  link (a plain Google Maps URL, which loads nothing until clicked). The old map failed with
  "can't load Google Maps correctly" (a key or billing problem), so test the key on the preview
  host.

**Seed images.** Until the client sends the originals, every seeded image (cards, value blocks,
the capability image, team portraits, partner and client logos, the NGO diagram) is cut from the old site's screenshots
(`apps/core/seed/images/`, 30 files, about 0.5 MB). They look right at
their displayed size but are small; replacing them is an upload in the admin (Phase 1 Q5).

### Phase 2 pages

Jobs (list and detail) and Search (dropdown, results page, highlighting) are designed in
`Phase_2/Phase2_Scope.md` §2 and move here when built.

## 5. JavaScript modules (Phase 1)

| Module | Responsibility | Day |
|---|---|---|
| `main.js` | The entry point (`<script type="module">` after Bootstrap's bundle); initialises each module | 5 |
| `modules/hero-slider.js` | Starts the Home carousel (6 s per slide) unless the visitor prefers reduced motion; pauses on hover and while keyboard focus is inside; shows a **Pause slides / Play slides** button (`aria-pressed`) that stops it until pressed again. Without JavaScript, or with reduced motion, the slides change only by the arrows and dots | 5 |
| `modules/read-more.js` | Cuts each `[data-read-more]` element to about nine lines and adds a **Read more / Show less** button (`aria-expanded`, `aria-controls`), only when the text is actually longer | 6 |
| `modules/http.js` | `fetch` wrapper: CSRF header from the cookie, JSON parsing, the `{ok, data, errors}` envelope, a timeout | 8 |
| `modules/contact-form.js` | Intercepts submit on any `[data-contact-form]`, posts through `http.js`, shows field errors and the success state; the form still works by normal POST if JS fails | 8 |
| `modules/cookie-consent.js` | The banner, the stored choice (`localStorage`, wrapped in `try/catch`), a `consent:granted` event, the "Cookie settings" link; injects the GA4 tag and the map iframe only after consent | 8 |

Conventions: ES modules, no globals, feature-detect and fail quietly, `data-*` attributes for
hooks, never inline event handlers. Module imports are relative (`./modules/hero-slider.js`);
Django's manifest storage serves them under their plain names, so a changed module reaches
browsers at their next cache refresh, not instantly. If that matters later, switch on the
storage's `support_js_module_import_aggregation`.

## 6. Accessibility and performance

- Semantic landmarks (`header`, `nav`, `main`, `footer`), one `h1` per page, a skip link.
- Contrast: gold on black passes; gold text on white uses `$dcs-gold-dark`.
- Images: `loading="lazy"` except the hero, explicit `width`/`height`, `alt` required in the admin
  for meaningful images (empty `alt` allowed for decorative ones).
- Slider: pauses on hover and focus, keyboard-operable controls, a pause button (moving content
  needs one), no auto-advance with `prefers-reduced-motion`.
- Fonts with `font-display: swap`; compressed CSS; nothing third-party before consent.
- Lighthouse targets on every Phase 1 page: Performance ≥ 90, Accessibility ≥ 90, SEO ≥ 95.

## 7. Cookie banner and analytics

Necessary cookies only by default (session, CSRF, the consent choice). **Accept** stores
`analytics` consent, loads GA4 (`GA_MEASUREMENT_ID` from `SiteSettings`, falling back to the
environment) and the Google Map. **Decline** loads neither. The footer's "Cookie settings" link
reopens the choice; withdrawing consent stops loading GA4 on the next page.
