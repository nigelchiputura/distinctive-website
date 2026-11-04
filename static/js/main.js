// Entry point (docs/frontend.md §5). An ES module, loaded after Bootstrap's bundle.
// Each feature finds its own [data-*] hooks and does nothing on pages without them.

import { initHeroSlider } from "./modules/hero-slider.js";
import { initReadMore } from "./modules/read-more.js";

initHeroSlider();
initReadMore();
