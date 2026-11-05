# Frontend

**Project-wide · revised 2026-11-03** (Day 2 as built: sampled brand colours, inline SVG icons,
Node 22; 2026-11-02: npm and SCSS at the repo root as in Consult 360, Phase 1 pages, Jobs and
Search designs moved to `Phase_2/Phase2_Scope.md`)

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
| Vendor assets | Bootstrap's JS bundle (`static/vendor/bootstrap/`, source-map line removed) and Open Sans `woff2` (`static/vendor/open-sans/`), copied from `node_modules` by `npm run vendor` and committed |
| Icons | Font Awesome Free SVGs, written by `npm run vendor` as inline partials in `templates/includes/icons/` (`{% include "includes/icons/phone.svg" %}`). No icon webfont to download; each icon takes the text colour |
| Fonts | Open Sans (the old site's face), self-hosted |

### Node on the dev machine only

```jsonc
// package.json (repo root)
{
  "private": true,
  "scripts": {
    "build:css": "sass static/scss/main.scss static/css/main.css --style=compressed --no-source-map --load-path=node_modules --quiet-deps --silence-deprecation=import",
    "watch:css": "sass static/scss/main.scss static/css/main.css --watch --no-source-map --load-path=node_modules --quiet-deps --silence-deprecation=import",
    "vendor": "node scripts/copy-vendor.mjs"
  },
  "engines": { "node": ">=22" },
  "devDependencies": {
    "@fontsource/open-sans": "5.3.0",
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
- `static/css/main.css` is committed. CI rebuilds it and fails on any difference, or if a
  `sourceMappingURL` slipped in (`deployment.md` §5).
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
@import "components/hero";
@import "components/section";
@import "components/cards";
@import "components/forms";
@import "components/footer";
@import "components/cookie-banner";
@import "pages/home";
@import "pages/about";
@import "pages/services";
@import "pages/contact";
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
| `$dcs-grey` | `#666` | Navbar links, muted text on white | 5.7:1 on white |
| `$dcs-grey-on-dark` | `#a6a6a6` | Copyright line on black (the old `#666` was 3.7:1) | 8.6:1 on black |
| `$dcs-text` | `#222` | Body text | — |
| `$dcs-gold` | `#d4af37` (exactly the old theme's) | Headings and links on dark, active-nav underline, CTA outline | 10:1 on black, **2.1:1 on white** |
| `$dcs-gold-dark` | `#86691a` | Gold **text** on light backgrounds (links, active nav) | 5.2:1 on white |
| `$dcs-gold-deeper` | `#6b5415` | Hover on `$dcs-gold-dark` links | — |
| `$dcs-white` | `#fff` | Light bands, navbar | — |
| `$dcs-navy`, `$dcs-blue` | placeholders | About "Our Story" gradient; sampled on Day 6 | — |
| Body font | Open Sans 400/600/700 | All text | — |

**The logo** is the file the client sent on 2026-11-03: `static/img/logo.png`, a transparent PNG
trimmed to 172 × 100 and reduced to 128 colours (3.9 KB). It shows at 60 px high, so on high-density
screens it is slightly soft; an SVG (or a PNG at least 2× the size) would make it crisp. Its gold
is a gradient around `#d2a22f`, close to the site's `#d4af37`, which stays as the old theme's.

Bootstrap overrides: `$primary: $dcs-gold`, `$body-color`, `$font-family-sans-serif`,
`$link-color: $dcs-gold-dark`, `$navbar-light-*`, `$btn-border-radius`, `$headings-color`.

## 3. Templates

```
base.html
 ├─ includes/_seo.html            <title>, meta description, canonical, OG/Twitter, JSON-LD
 ├─ includes/_topbar.html         phones, email, social icons (SiteSettings)
 ├─ includes/_navbar.html         logo + nav items from the context processor
 ├─ <main id="main"> {% block content %}
 ├─ includes/_footer.html         "Reach Us", footer nav, copyright, "Cookie settings" link
 └─ includes/_cookie_banner.html
```

`includes/_section.html` renders a `PageSection` by `section_type`, with `id="{{ section.anchor }}"`:

| `section_type` | Look (from the old site) |
|---|---|
| `hero_text` | Full-width image band with a large heading |
| `intro_dark` | Black band, gold heading, white text ("What We Do") |
| `band_light` / `band_dark` | Alternating bands used on Services; heading left- or right-aligned |
| `two_column` | "Our Story" style: heading and short text left, long text right |
| `value_block` | Image one side, heading and paragraph the other; alternates |
| `cta` | A centred line and an outlined gold button ("Get In Touch") |

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

1. Hero slider, 3 slides (`HeroSlide`): team photo with "Distinctive Consultancy Services —
   Bringing excellence into your world."
2. Charcoal band with six service cards: Industrial / Employee Relations, HR Audits, Talent
   Acquisition, People Strategy, Research Surveys, Organisational Design. Framed image, gold
   title, short blurb (`Service.show_on_home`); each links to `/services/#<anchor>`.
3. CTA: "Get the best specialised business consultancy services in Africa." + outlined gold
   "Get In Touch" → `/contact/`.
4. Two value blocks on white: **People Centred** and **Proactive**, image alternating.

### About

1. Hero image with "Bringing Excellence Into Your World!".
2. **Our Story:** navy-to-blue gradient band, short intro left, long text right (bold key
   phrases).
3. **Strategic Partners:** centred logos with captions (Emergence Growth, Bindura University of
   Science Education) (`Partner`, kind = partner).
4. **Capability Analysis** (charcoal band, with image); **Value Driven and Capacity Building**
   (right-aligned heading).
5. **Our Leadership:** four-column grid (two on tablet, one on mobile), circular portraits, name,
   title in grey, bio. Eight people; long bios collapse behind "Read more" on mobile. Social
   icons per person where provided. The old bios were justified and cramped: use left-aligned
   text at a comfortable line length.

### Services

1. A static hero with anchor navigation to each service (the old site had a 13-slide slider).
2. "What We Do" intro on black.
3. Alternating light/dark service bands, each with its anchor: Industrial / Employee Relations;
   Rightsizing / Organisational Design; Services for the NEC; Research Surveys; Learning and
   Development (Training); Organizational Development; HR Audits; Organizational Design and
   Restructuring; Team Building; Outsourced HR Services; Talent Acquisition; People Strategy; NGO
   Capacity Development Partners (with its diagram image).
4. "Some of our corporate clients": a logo grid of 10 (`Partner`, kind = client).
5. The gold "Get In Touch With Us" block: a general enquiry form (first name, last name, email,
   message) posting to the contact service with `source_page=services`; button "Send enquiry".

### Contact

- Black band: "Get In Touch!" form (Name, Email Address, Message, Submit) left; "Reach Us" right,
  including the vacancies line until Phase 2 ("Send your CV to recruitment@…", from
  `SiteSettings.recruitment_email`).
- Map band: an interactive Google Map (Maps Embed API iframe, key restricted by HTTP referrer),
  injected **only after cookie consent**. Before consent: the address and a "Get directions"
  link (a plain Google Maps URL, which loads nothing until clicked). The old map failed with
  "can't load Google Maps correctly" (a key or billing problem), so test the key on the preview
  host.

### Phase 2 pages

Jobs (list and detail) and Search (dropdown, results page, highlighting) are designed in
`Phase_2/Phase2_Scope.md` §2 and move here when built.

## 5. JavaScript modules (Phase 1)

| Module | Responsibility |
|---|---|
| `http.js` | `fetch` wrapper: CSRF header from the cookie, JSON parsing, the `{ok, data, errors}` envelope, a timeout |
| `contact-form.js` | Intercepts submit on any `[data-contact-form]`, posts through `http.js`, shows field errors and the success state; the form still works by normal POST if JS fails |
| `cookie-consent.js` | The banner, the stored choice (`localStorage`, wrapped in `try/catch`), a `consent:granted` event, the "Cookie settings" link; injects the GA4 tag and the map iframe only after consent |
| `main.js` | Imports and initialises the above; initialises Bootstrap components (carousel, collapse) |

Conventions: ES modules (`<script type="module">`), no globals, feature-detect and fail quietly,
`data-*` attributes for hooks, never inline event handlers.

## 6. Accessibility and performance

- Semantic landmarks (`header`, `nav`, `main`, `footer`), one `h1` per page, a skip link.
- Contrast: gold on black passes; gold text on white uses `$dcs-gold-dark`.
- Images: `loading="lazy"` except the hero, explicit `width`/`height`, `alt` required in the admin
  for meaningful images (empty `alt` allowed for decorative ones).
- Slider: pauses on hover and focus, keyboard-operable controls, no auto-advance with
  `prefers-reduced-motion`.
- Fonts with `font-display: swap`; compressed CSS; nothing third-party before consent.
- Lighthouse targets on every Phase 1 page: Performance ≥ 90, Accessibility ≥ 90, SEO ≥ 95.

## 7. Cookie banner and analytics

Necessary cookies only by default (session, CSRF, the consent choice). **Accept** stores
`analytics` consent, loads GA4 (`GA_MEASUREMENT_ID` from `SiteSettings`, falling back to the
environment) and the Google Map. **Decline** loads neither. The footer's "Cookie settings" link
reopens the choice; withdrawing consent stops loading GA4 on the next page.
