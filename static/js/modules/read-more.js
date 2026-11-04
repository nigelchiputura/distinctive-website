// Long text shortened behind a "Read more" button (team bios on About).
//
// Each [data-read-more] element is cut to a few lines by CSS once this module adds
// .is-collapsed; the button appears only if the text is actually longer than that. Without
// JavaScript nothing is cut, so the whole text is always readable.

export function initReadMore(root = document) {
  root.querySelectorAll("[data-read-more]").forEach((el) => {
    el.classList.add("is-collapsed");
    if (el.scrollHeight <= el.clientHeight + 4) {
      el.classList.remove("is-collapsed"); // short enough: no button
      return;
    }
    const button = document.createElement("button");
    button.type = "button";
    button.className = "read-more__toggle";
    button.setAttribute("aria-expanded", "false");
    if (el.id) button.setAttribute("aria-controls", el.id);
    button.textContent = "Read more";
    button.addEventListener("click", () => {
      const expanded = el.classList.toggle("is-collapsed") === false;
      button.setAttribute("aria-expanded", String(expanded));
      button.textContent = expanded ? "Show less" : "Read more";
    });
    el.after(button);
  });
}
