// The Home hero slider (templates/includes/_hero_slider.html).
//
// Bootstrap's carousel does the sliding; this decides when it moves on by itself:
// - never, if the visitor prefers reduced motion (the arrows and dots still work);
// - not while the pointer is over it (Bootstrap's "hover" pause) or keyboard focus is inside it;
// - not after the visitor presses the pause button, until they press it again.

const INTERVAL_MS = 6000;

export function initHeroSlider(root = document) {
  const el = root.querySelector("[data-hero-slider]");
  const Carousel = window.bootstrap?.Carousel;
  if (!el || !Carousel) return;

  const carousel = Carousel.getOrCreateInstance(el, { interval: INTERVAL_MS, pause: "hover", ride: false });

  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  if (reducedMotion) return;

  const button = el.querySelector("[data-hero-pause]");
  const label = el.querySelector("[data-hero-pause-label]");
  let pausedByVisitor = false;

  const play = () => {
    if (!pausedByVisitor) carousel.cycle();
  };

  el.addEventListener("focusin", () => carousel.pause());
  el.addEventListener("focusout", (event) => {
    if (!el.contains(event.relatedTarget)) play();
  });

  if (button && label) {
    button.hidden = false;
    button.addEventListener("click", () => {
      pausedByVisitor = !pausedByVisitor;
      button.setAttribute("aria-pressed", String(pausedByVisitor));
      label.textContent = pausedByVisitor ? "Play slides" : "Pause slides";
      if (pausedByVisitor) carousel.pause();
      // Focus is on the button, so cycling restarts when focus leaves the slider.
    });
  }

  play();
}
