// Fades [data-reveal] elements in as they scroll into view. Elements are hidden only after
// this module has started (html.reveal-ready), so without JavaScript, or with an old browser,
// everything simply shows. data-reveal-delay="n" staggers a row of cards by n steps. With
// reduced motion the CSS shows everything at once.

const STEP_SECONDS = 0.08;
const MAX_STEPS = 6;

export function initReveal(root = document) {
  const items = root.querySelectorAll("[data-reveal]");
  if (!items.length || !("IntersectionObserver" in window)) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.12 },
  );

  items.forEach((item) => {
    const steps = Math.min(Number(item.dataset.revealDelay) || 0, MAX_STEPS);
    if (steps) item.style.setProperty("--reveal-delay", `${steps * STEP_SECONDS}s`);
    observer.observe(item);
  });
  document.documentElement.classList.add("reveal-ready");
}
