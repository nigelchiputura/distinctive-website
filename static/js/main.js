// Entry point (docs/frontend.md §5). An ES module, loaded after Bootstrap's bundle.
// Each feature finds its own [data-*] hooks and does nothing on pages without them.

import { initBackToTop } from "./modules/back-to-top.js";
import { initBioDialogs } from "./modules/bio-dialog.js";
import { initContactForms } from "./modules/contact-form.js";
import { initCookieConsent } from "./modules/cookie-consent.js";
import { initHeroSlider } from "./modules/hero-slider.js";
import { initNavbar } from "./modules/navbar.js";
import { initReveal } from "./modules/reveal.js";
import { initThemeToggle } from "./modules/theme.js";

initThemeToggle();
initNavbar();
initReveal();
initCookieConsent();
initHeroSlider();
initBioDialogs();
initContactForms();
initBackToTop();
