// The back-to-top button. Without JavaScript it is a plain link to #top that is always shown;
// with it, it appears after the visitor has scrolled down, scrolls up smoothly (instantly with
// reduced motion) and moves keyboard focus to the logo, the first thing on the page.

const SHOW_AFTER = 600; // pixels scrolled

export function initBackToTop(root = document) {
  const link = root.querySelector("[data-back-to-top]");
  if (!link) return;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let ticking = false;

  const update = () => {
    link.classList.toggle("is-visible", window.scrollY > SHOW_AFTER);
    ticking = false;
  };

  link.classList.add("is-enhanced");
  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(update);
      }
    },
    { passive: true },
  );
  update();

  link.addEventListener("click", (event) => {
    event.preventDefault();
    window.scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" });
    const first = root.querySelector(".navbar-brand");
    if (first) first.focus({ preventScroll: true });
  });
}
