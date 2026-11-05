# Frontend

**Project-wide · revised 2026-11-04** (Day 9 as built: light and dark themes, the modernised
components, motion, back to top; Day 8 as built: Contact, the enquiry forms, cookie consent;
Day 7 as built: the Services page; the font is Nunito Sans;
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
  Day 10, import only the Bootstrap partials in use.

## 2. SCSS architecture

`main.scss` order matters:

```scss
@import "tokens";                            // 1. $dcs-* brand tokens
@import "variables";                         // 2. Bootstrap variable overrides (use the tokens)
@import "bootstrap/scss/bootstrap";          // 3. Bootstrap, themed by 1–2
@import "theme";                             // 4. light and dark custom properties (Day 9, §8)
@import "fonts";                             // 5. our rules
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
@import "components/team";                   // Day 6: Our Leadership; Day 9: the bio dialog
@import "components/services";               // Day 7: the Services page
@import "components/forms";                  // Day 8: the enquiry forms, on black and on gold
@import "components/contact";                // Day 8: Reach Us, the gold band, the map band
@import "components/cookie-banner";          // Day 8
@import "components/error-page";             // Day 10: the 404 and 500 pages
// pages/* only if a page ever needs rules of its own (none has so far).
```

`@import` is fine for now: `--silence-deprecation=import` quiets Dart Sass's warning about our own
`@import`s, and `--quiet-deps` hides Bootstrap's. The build prints no warnings; keep it that way
(no `darken()`/`lighten()`: add a token instead). Migrate to `@use` when Bootstrap's Sass supports
it cleanly. Partials are added to `main.scss` on the day their component arrives.

**Colours only through tokens.** SCSS uses `$dcs-*`; `_tokens.scss` also emits them as `--dcs-*`
custom properties on `:root` for the few places JS or inline styles need them. No raw hex values
outside `_tokens.scss`. **Colours that change with the theme** are the semantic custom properties
in `_theme.scss` (`--dcs-page`, `--dcs-surface`, `--dcs-text`, `--dcs-text-muted`,
`--dcs-heading`, `--dcs-accent`, `--dcs-border`, `--dcs-shadow` …), set once for light and once
for dark (§8); components on light bands use those, never a fixed white or black.

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
| `$dcs-gold` | `#d4af37` (exactly the old theme's) | Headings and links on dark, active-nav underline, CTA outline, the Services enquiry band (black text on it, 10:1) | 10:1 on black, **2.1:1 on white** |
| `$dcs-gold-dark` | `#86691a` | Gold **text** on light backgrounds (links, active nav) | 5.2:1 on white |
| `$dcs-gold-deeper` | `#6b5415` | Hover on `$dcs-gold-dark` links | — |
| `$dcs-white` | `#fff` | Light bands, navbar | — |
| `$dcs-gold-light` | `#e8c766` | The light end of gold gradients (buttons, the enquiry band, headings in the hero) | black text 12.8:1 |
| `$dcs-paper` | `#faf8f3` | Warm off-white: light bands' gradient, form fields, value blocks | `$dcs-grey` 5.4:1, `$dcs-gold-dark` 4.9:1 |
| `$dcs-ink` / `$dcs-ink-soft` / `$dcs-ink-raised` | `#0e0f11` / `#1a1d21` / `#23272c` | Dark theme: page, light bands, cards | — |
| `$dcs-text-on-ink` / `$dcs-muted-on-ink` | `#e9e7e2` / `#a9adb3` | Dark theme: body and muted text | 15.5:1 on the page; muted 6.6:1 on cards |
| `$dcs-error` | `#b42318` | Form errors, light theme | 6.6:1 on white, 6.2:1 on paper |
| `$dcs-error-on-dark` | `#ff8a80` | Form errors on black and in the dark theme | 9.2:1 on black, 6.6:1 on dark cards |
| `$dcs-radius-sm` … `$dcs-radius-pill` | 0.5 / 1 / 1.5 rem, pill | Corners: fields 0.75 rem, cards 1.5 rem, buttons and chips pill | — |
| `$dcs-ease`, `$dcs-duration` | `cubic-bezier(.2,.7,.2,1)`, 0.3 s | Every transition | — |
| `$dcs-navy` → `$dcs-blue` | `#02070b` → `#1f5fa8` | About "Our Story" gradient (sampled on Day 6). The old band ran on to `#2a85d6`; it stops darker here | white text 6.4:1 or better throughout (the old end was 3.9:1) |
| `$dcs-font-sans` | Nunito Sans 400/600/700, then system fonts | All text, site and admin (`admin.scss` imports `_fonts.scss` too) | — |

**The logo** is the file the client sent on 2026-11-03: `static/img/logo.png`, a transparent PNG
trimmed to 172 × 100 and reduced to 128 colours (3.9 KB). It shows at 60 px high, so on high-density
screens it is slightly soft; an SVG (or a PNG at least 2× the size) would make it crisp. Its gold
is a gradient around `#d2a22f`, close to the site's `#d4af37`, which stays as the old theme's.

Bootstrap overrides: `$primary: $dcs-gold`, `$body-color`, `$font-family-sans-serif`,
`$link-color: $dcs-gold-dark`, `$navbar-light-*`, `$headings-color`, and (Day 9) rounded corners:
`$border-radius*`, pill `$btn-border-radius*` with more padding and a transition, 0.75 rem
`$input-border-radius`, 1 rem `$dropdown-border-radius`. At runtime `_theme.scss` points
Bootstrap's `--bs-body-bg`, `--bs-body-color`, `--bs-border-color` and `--bs-link-color-rgb` at
the theme's colours.

**The logo** has a second copy for dark backgrounds, `static/img/logo-dark.png` (Day 9): the
black lettering and ring made light, the gold untouched. The navbar shows the one that fits the
theme; the footer always uses the light one.

## 3. Templates

```
base.html
 ├─ js/theme-init.js              applies a chosen Light or Dark theme before the first paint (Day 9)
 ├─ includes/_seo.html            <title>, meta description, canonical, OG/Twitter, JSON-LD (Day 10)
 ├─ includes/_topbar.html         phones, email, social icons (site_info)
 ├─ includes/_navbar.html         both logos, nav items, includes/_theme_toggle.html
 ├─ <main id="main"> {% block main %}{% block content %}   pages fill "content";
 │                                 a layout can wrap it by overriding "main"
 ├─ includes/_footer.html         logo and blurb, Reach Us (_contact_list.html), Quick Links, copyright, "Cookie settings"
 ├─ includes/_cookie_banner.html  only when GA4 or the map is set up (consent_needed); hidden until JS shows it
 ├─ <template data-icon>s         icons the scripts copy into what they build (the dialog's ×, arrows, ticks)
 ├─ the back-to-top link          href="#top" (<body id="top">)
 └─ Bootstrap's bundle (defer), then js/main.js (type="module")

pages/page.html                   any page: a visually hidden h1 unless the first section is a hero_text band,
                                  then includes/_section.html per section
pages/home.html                   extends page.html; its top is includes/_hero_slider.html
includes/_section.html            one PageSection, by section_type (table below)
includes/_service_card.html       one offerings.Service on Home
includes/_logo_grid.html          partner or client logos (pages.Partner)
includes/_team_card.html          one team.TeamMember
includes/_image.html              an admin image with its stored width/height and alt text
includes/_enquiry_form.html       ContactForm or EnquiryForm: labels, an error slot per field, the honeypot
includes/_section_head.html       a section's label and heading, with the gold bar under it (Day 9)
includes/_contact_list.html       address, phone, email, hours (and on Contact the vacancies line) as icon rows (Day 9)
includes/_theme_toggle.html       the System / Light / Dark menu (Day 9)
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

| `section_type` | Look (as built on Day 9; the old site's structure, modernised) |
|---|---|
| `hero_text` | Full-width band, the page's `h1` when it's the first section: a photo behind a dark overlay, or without one (About, Services and Contact today) the same drifting black-and-gold gradient as Home's slider without a photo, with faint diagonal lines; label, heading and text fade up on load |
| `intro_dark` / `band_dark` | Black or charcoal band with a soft gold glow in one corner; label, white heading with a gold bar, text; an optional framed image beside it |
| `band_light` | Light band (white to warm paper; dark grey in the dark theme), the same layout |
| `two_column` | "Our Story": the navy-to-blue band with a gold glow; label, heading and the **short text** (`intro`) left, the body in a frosted card right |
| `value_block` | Image in a rounded frame with a gold offset outline (which shifts on hover), label, heading and text beside it; consecutive value blocks share one flat paper background |
| `service_bands` | The Services page: numbered chips (`01`–`13`) linking to every service, then each service in its own band, alternating black and light, with a large gold number above its title and `id="<anchor>"`; list items get gold ticks, long lists two columns. A service's image shows beside its text only when "show the image on the Services page" is ticked (the NGO diagram) |
| `service_cards` | Charcoal band with the services ticked "show on Home" (at most six): frosted cards with the image in a rounded frame, gold title, summary and "Learn more →"; the whole card is the link, and it lifts with a gold edge on hover. Card titles are `h2` when the section has no heading, `h3` under one |
| `partners` / `clients` | Light band; each logo on a white tile (white in both themes, since the logos are made for it), scaled into the same box without cropping, caption below; linked tiles lift on hover. Rows are centred, so ten clients sit five and five |
| `team` | Light band; a card per person: photo in a gold ring, name, job title in gold, the bio cut to five lines with **Read full bio** (the dialog, §5), LinkedIn and Facebook as round buttons |
| `cta` | A rounded panel with a gold glow on black: label, line, a filled gold button with an arrow |
| `contact_form` | Contact: the drifting black-and-gold gradient band; the label, heading ("Get In Touch!") and form in a frosted card on the left; on the right a gold-edged **Reach Us** card with icon rows for the address, phone, email, hours and the vacancies line, all from `SiteSettings` (the section's body, if any, goes under them). Button label from the section, default "Submit" |
| `enquiry_form` | Services: gold gradient band; label, black heading ("Get In Touch With Us") and text on the left, the enquiry form in a card (following the theme) on the right; button label default "Send enquiry" |
| `map` | Light band: a card with the label, heading ("Find Us"), the address and **Get directions**; beside it, when `GOOGLE_MAPS_EMBED_KEY` is set, a rounded frame that holds the map once the visitor accepts cookies (until then a map icon, a note and "Cookie settings") |

Every section has an optional **label** (`PageSection.eyebrow`, Day 9): a small uppercase gold
pill above the heading ("What we do", "The team"), seeded for every section.

**Forms.** Labels above fields, "All fields are required." above them, and each field's error as
a sentence under it (`aria-invalid` and `aria-describedby` link the two), so errors never rely
on colour. General errors (the rate limit, a network failure) go in an alert above the fields.
Name and email (Contact), first and last name (Services) share a row from 768 px. Messages are
capped at 5,000 characters. Since Day 9 the fields are rounded (0.75 rem) with a gold focus glow;
on the black Contact band they are translucent, in the Services card they follow the theme. The
submit button is filled gold with an arrow, and the thank-you fades in with a tick.

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
- **Navbar (sticky, frosted; white or dark with the theme):** logo left; **Phase 1:** Home, About
  Us, Services, Contact Us, from `NavigationService`, then the theme toggle. Phase 2 adds Jobs and
  the search icon. Gold marks hover and the current page, which also gets a gold underline that
  grows in, and `aria-current="page"` (colour alone isn't enough). Below 992 px the links
  collapse behind the toggler; the theme toggle stays beside it.
- **Footer (Day 9):** three columns on a dark gradient with a gold line along the top: the light
  logo, tagline, blurb and social buttons; **Reach Us** as icon rows (62 Mutare Road, Beverly,
  Msasa, Harare; phone; email; hours 8:00am–4:30pm Mon–Fri); **Quick Links**. A bottom line with
  copyright and "Cookie settings". All values from `SiteSettings`.
- **Not carried over:** the WordPress "Categories" footer widget, the RSS icon, the old sidebar
  search box, and the "Designed by" credit unless the client wants it (Phase 1 Q7).

### Home

1. Hero slider (`HeroSlide`): the first slide's heading is the page's `h1` ("Distinctive
   Consultancy Services", in a gold gradient, "Bringing excellence into your world."). Since
   2026-11-04 the slide shows the **team photo** the owner sent (seeded as `team-photo.jpg`,
   1600 px wide, about 280 KB, loaded first with `fetchpriority="high"`). A slide with a photo
   (`hero__slide--photo`) is taller (up to 80 vh), puts its text at the top over the darkened
   trees, and crops the photo from the top (`object-position: center 12%`), so the team's faces
   stay clear at every width; a soft gold glow sits over the photo. A slide without a photo
   shows the drifting black-and-gold gradient. With no slides at all, a visually hidden `h1`
   keeps the page's outline.
2. **Our services · What We Do** (label and heading added on Day 9): six service cards (a
   `service_cards` section): Industrial / Employee
   Relations, HR Audits, Talent Acquisition, People Strategy, Research Surveys, Organisational
   Design. Framed image, gold title, short blurb; each links to `/services/#<anchor>`. Card images
   are fitted inside a fixed 3:2 frame without cropping (`object-fit: contain`), because several
   have words in them.
3. CTA, label "Let's talk": "Get the best specialised business consultancy services in
   Africa." + a filled gold "Get In Touch →" to `/contact/`, in a rounded panel.
4. Two value blocks, label "Our values": **People Centred** and **Proactive**, framed images
   alternating sides.

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
   with gaps). Since Day 9 a long bio is cut to five lines with **Read full bio**, which opens it in
   a dialog, so the cards line up; without JavaScript every bio shows in full.

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
4. `enquiry_form` **Get In Touch With Us** (Day 8): the gold block with a general enquiry form
   (first name, last name, email, message) posting to `/contact/`, saved with
   `source_page=services`; button "Send enquiry".

### Contact

As built on Day 8, with a page hero added on Day 9: three sections (`hero_text` **Contact Us**,
which is the page's `h1`, with a line inviting a message, call or visit; `contact_form`; `map`).

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
their displayed size but are small; replacing them is an upload in the admin (Phase 1 Q5). The
31st seed image is the team photo behind Home's hero, sent by the owner on 2026-11-04.

### Phase 2 pages

Jobs (list and detail) and Search (dropdown, results page, highlighting) are designed in
`Phase_2/Phase2_Scope.md` §2 and move here when built.

## 5. JavaScript modules (Phase 1)

| Module | Responsibility | Day |
|---|---|---|
| `main.js` | The entry point (`<script type="module">` after Bootstrap's bundle); initialises each module | 5 |
| `modules/hero-slider.js` | Starts the Home carousel (6 s per slide) unless the visitor prefers reduced motion; pauses on hover and while keyboard focus is inside; shows a **Pause slides / Play slides** button (`aria-pressed`) that stops it until pressed again. Without JavaScript, or with reduced motion, the slides change only by the arrows and dots | 5 |
| `theme-init.js` (not a module) | In `<head>`, before the stylesheet: applies a stored Light or Dark choice as `data-theme` on `<html>` and adds the `js` class, so there is no flash of the wrong theme | 9 |
| `modules/theme.js` | Shows the toggle, marks the current choice (`aria-pressed`, the button's icon and `aria-label`), stores Light or Dark in `localStorage` (`dcs-theme`; System removes it), applies it at once and fires `theme:changed` | 9 |
| `modules/reveal.js` | Fades `[data-reveal]` elements up as they enter the viewport (`IntersectionObserver`), staggered by `data-reveal-delay`; adds `reveal-ready` to `<html>` first, and only then does CSS hide anything | 9 |
| `modules/navbar.js` | Adds `is-scrolled` to the navbar (a shadow and a smaller logo) once the page has scrolled | 9 |
| `modules/bio-dialog.js` | Cuts each long `[data-bio]` to five lines and adds **Read full bio**, which opens the person's photo, name, title and whole bio in one shared `<dialog>`; Escape, the × or a click outside close it, and focus returns to the button. Replaced Day 6's `read-more.js` | 9 |
| `modules/back-to-top.js` | Shows the back-to-top link after 600 px of scrolling; scrolls up (smoothly unless reduced motion) and moves focus to the logo | 9 |
| `modules/http.js` | `postForm()`: `fetch` with the CSRF header (from the cookie, else the form's token), `X-Requested-With`, a 15 s timeout; every reply, network failures and Django's HTML 403/500 included, comes back as the `{ok, data, errors}` envelope with a plain-English message | 8 |
| `modules/contact-form.js` | Intercepts submit on any `[data-contact-form]`, posts through `http.js` (the button is disabled with `aria-busy` meanwhile), puts each error under its field and moves focus to the first, or shows the alert for general errors; on success the form is replaced by the thank-you (`role="status"`, focused). The form still works by normal POST if JS fails | 8 |
| `modules/cookie-consent.js` | The banner, the stored choice (`localStorage`, wrapped in `try/catch`), a `consent:granted` event, the "Cookie settings" link; injects the GA4 tag and the map iframe only after consent | 8 |

Conventions: ES modules, no globals, feature-detect and fail quietly, `data-*` attributes for
hooks, never inline event handlers. Module imports are relative (`./modules/hero-slider.js`);
Django's manifest storage serves them under their plain names, so a changed module reaches
browsers at their next cache refresh, not instantly. If that matters later, switch on the
storage's `support_js_module_import_aggregation`.

## 6. Accessibility and performance

Day 9 additions: the theme toggle is a labelled button with a menu whose options say which is
pressed; the bio dialog is a native modal `<dialog>` labelled by the person's name; the back-to-top
link has a label and moves focus; every colour pair in both themes is AA or better (the token
table lists the ratios); motion respects `prefers-reduced-motion`; nothing is hidden without
JavaScript.

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

**As built on Day 8** (`cookie-consent.js`):

- No Google address is in any page's HTML. The GA4 id is `data-ga-id` on the banner and the map
  is `data-map-key` and `data-map-query` on its frame; the script and iframe addresses are built in
  JavaScript after **Accept** (a test checks all four pages, `apps/core/tests/test_consent.py`).
  "Get directions" is a plain link to Google Maps, which loads nothing until clicked.
- The banner is a card floating bottom left (since Day 9; on phones it spans the width), black
  with a gold edge, **Accept** (filled gold) and **Decline** (outlined). It is `hidden` in the HTML and shown by the script, so without
  JavaScript nothing asks and nothing loads. It isn't rendered at all when neither GA4 nor the
  map is set up (`consent_needed`), since there would be nothing to ask about.
- The choice is `{"version": 1, "analytics": true|false, "at": …}` in `localStorage` under
  `dcs-cookie-consent`, read and written inside `try/catch`; with storage blocked it lasts for
  the page and the banner asks again on the next. Raising `VERSION` asks everyone again.
- On Accept: the GA4 tag, the map iframe (Maps Embed API `place` mode, lazy, with a title), and a
  `consent:granted` event on `document`. On later pages both load straight away.
- "Cookie settings" (footer, and in the map note) reopens the banner and moves focus to Accept;
  choosing returns focus to the link, and Escape closes it once a choice exists. Declining after
  accepting sets GA's own `ga-disable-<id>` switch, deletes the `_ga` cookies and fires
  `consent:declined`; the map stays until the next page.

## 8. Themes, components and motion (Day 9)

**Themes.** Three choices: **System** (the default: CSS follows `prefers-color-scheme`),
**Light** and **Dark**. `_theme.scss` defines the semantic custom properties twice, in a light
mixin on `:root` and a dark mixin applied by `:root[data-theme="dark"]` or, with no choice made,
by `@media (prefers-color-scheme: dark)` on `:root:not([data-theme="light"])`. The choice is stored
in `localStorage` (`dcs-theme`), not a cookie; it is a display setting the visitor makes
themselves, so it doesn't need cookie consent. `theme-init.js` applies it in `<head>` before the
first paint; without JavaScript the system setting still applies and the toggle stays hidden.

The **drifting gold gradient** (the `dcs-hero-glow` mixin in `_hero.scss`: two gold radial
glows over black-to-charcoal, moving over 18 s) is the background of every hero without a photo
and of the Contact form's band.

What changes with the theme: the page, light bands, cards, text, headings, borders, shadows, the
navbar's frosted background, form fields on light bands and the logo. What doesn't: the black,
charcoal and navy bands, the gold enquiry band, the footer, the heroes and the cookie card, which
are dark (or gold) by design in both, and the logo tiles, which stay white for the logos' sake.

**Components.** Section labels (`.eyebrow`), headings with a gold bar (`.section-head`), frosted
`.glass-card`s on dark bands, `.surface-card`s that follow the theme, `.framed-image`s with a
gold offset outline, `.contact-list` icon rows, `.social-circle` buttons, pill chips on Services,
rounded buttons (`.btn-gold` filled with a gold gradient and glow, `.btn-outline-gold` on dark,
`.btn-outline-gold-dark` on light), the floating cookie card and the back-to-top button. Bands
use gradients with a soft gold radial glow in a corner instead of flat colour.

**Motion.** Scroll reveal (`reveal.js`, 0.7 s fade-up, cards staggered by 80 ms); hover lifts on
cards, tiles, chips and buttons; arrows that nudge on hover; image zoom in service cards; the
navbar underline that grows in; the hero's drifting gold light (18 s) and its text fading up on
load; the dialog and cookie card fading in. With `prefers-reduced-motion: reduce` there is no
movement: reveals show at once, animations last 0.01 ms, and back to top jumps instead of
scrolling. Printing shows everything and hides the toggle, cookie card and back to top.
