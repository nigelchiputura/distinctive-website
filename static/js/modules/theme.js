// The navbar's System / Light / Dark toggle (docs/frontend.md §8). "System" removes the
// choice, so CSS follows prefers-color-scheme; Light or Dark is kept in localStorage and set as
// data-theme on <html> (theme-init.js applies it before the first paint on later pages). A
// display preference the visitor sets themselves, so it needs no cookie consent.

const STORAGE_KEY = "dcs-theme";
const LABELS = { system: "System", light: "Light", dark: "Dark" };

export function storedTheme() {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    return value === "light" || value === "dark" ? value : "system";
  } catch {
    return "system";
  }
}

function applyTheme(choice) {
  const root = document.documentElement;
  if (choice === "system") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", choice);
}

function saveTheme(choice) {
  try {
    if (choice === "system") window.localStorage.removeItem(STORAGE_KEY);
    else window.localStorage.setItem(STORAGE_KEY, choice);
  } catch {
    // storage blocked: the choice lasts for this page only
  }
}

function showChoice(toggle, choice) {
  toggle.querySelectorAll("[data-theme-choice]").forEach((option) => {
    option.setAttribute("aria-pressed", String(option.dataset.themeChoice === choice));
  });
  toggle.querySelectorAll("[data-theme-icon]").forEach((icon) => {
    icon.hidden = icon.dataset.themeIcon !== choice;
  });
  const button = toggle.querySelector("[data-theme-button]");
  if (button) button.setAttribute("aria-label", `Colour theme: ${LABELS[choice]}`);
}

export function initThemeToggle(root = document) {
  root.querySelectorAll("[data-theme-toggle]").forEach((toggle) => {
    toggle.hidden = false;
    showChoice(toggle, storedTheme());
    toggle.addEventListener("click", (event) => {
      const option = event.target.closest("[data-theme-choice]");
      if (!option) return;
      const choice = option.dataset.themeChoice;
      saveTheme(choice);
      applyTheme(choice);
      showChoice(toggle, choice);
      document.dispatchEvent(new CustomEvent("theme:changed", { detail: { choice } }));
    });
  });
}
