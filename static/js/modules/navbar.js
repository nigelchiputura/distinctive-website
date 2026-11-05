// Gives the sticky navbar a shadow (and a slightly smaller logo) once the page has scrolled.

export function initNavbar(root = document) {
  const navbar = root.querySelector("[data-navbar]");
  if (!navbar) return;
  let ticking = false;
  const update = () => {
    navbar.classList.toggle("is-scrolled", window.scrollY > 8);
    ticking = false;
  };
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
}
