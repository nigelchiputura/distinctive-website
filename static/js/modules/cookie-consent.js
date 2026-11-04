// Cookie consent (docs/frontend.md §7). Nothing from Google loads until the visitor presses
// "Accept": this module builds the GA4 tag and the Contact map's iframe only then, from data
// attributes, so neither address is in the page before. The choice is kept in localStorage;
// if storage is blocked it lasts for this page only, and the banner asks again on the next.

const STORAGE_KEY = "dcs-cookie-consent";
const VERSION = 1; // raise when what "Accept" covers changes, so everyone is asked again

let pageChoice = null;

export function readChoice() {
  try {
    const stored = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "null");
    if (stored && stored.version === VERSION && typeof stored.analytics === "boolean") {
      return stored;
    }
  } catch {
    // storage blocked or the value unreadable: fall back to this page's choice
  }
  return pageChoice;
}

function saveChoice(analytics) {
  pageChoice = { version: VERSION, analytics, at: new Date().toISOString() };
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(pageChoice));
  } catch {
    // kept for this page only
  }
  return pageChoice;
}

function loadAnalytics(id) {
  if (!id) return;
  window[`ga-disable-${id}`] = false;
  if (document.querySelector("script[data-ga4]")) return;
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments); // gtag.js expects the arguments object itself
  }
  gtag("js", new Date());
  gtag("config", id);
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
  script.dataset.ga4 = "";
  document.head.append(script);
}

function stopAnalytics(id) {
  if (id) window[`ga-disable-${id}`] = true; // GA's own switch: stops it on this page too
  const host = window.location.hostname;
  const parent = host.split(".").slice(-3).join(".");
  const domains = ["", `; domain=${host}`, `; domain=.${host}`, `; domain=.${parent}`];
  document.cookie
    .split(";")
    .map((part) => part.split("=")[0].trim())
    .filter((name) => name === "_ga" || name.startsWith("_ga_") || name === "_gid")
    .forEach((name) => {
      domains.forEach((domain) => {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/${domain}`;
      });
    });
}

function loadMaps(root) {
  root.querySelectorAll("[data-consent-map]").forEach((frame) => {
    const { mapKey, mapQuery, mapTitle } = frame.dataset;
    if (!mapKey || !mapQuery || frame.querySelector("iframe")) return;
    const iframe = document.createElement("iframe");
    const params = new URLSearchParams({ key: mapKey, q: mapQuery });
    iframe.src = `https://www.google.com/maps/embed/v1/place?${params}`;
    iframe.title = mapTitle || "Map";
    iframe.loading = "lazy";
    iframe.referrerPolicy = "no-referrer-when-downgrade"; // the key is restricted by referrer
    iframe.allowFullscreen = true;
    frame.append(iframe);
    frame.querySelectorAll("[data-map-note]").forEach((note) => {
      note.hidden = true;
    });
  });
}

export function initCookieConsent(root = document) {
  const banner = root.querySelector("[data-cookie-banner]");
  if (!banner) return;
  const gaId = banner.dataset.gaId || "";
  let opener = null;

  const grant = () => {
    loadAnalytics(gaId);
    loadMaps(root);
    document.dispatchEvent(new CustomEvent("consent:granted"));
  };

  const open = (from) => {
    opener = from || null;
    banner.hidden = false;
    if (opener) banner.querySelector("[data-consent]").focus();
  };

  const close = () => {
    banner.hidden = true;
    if (opener) opener.focus();
    opener = null;
  };

  banner.addEventListener("click", (event) => {
    const button = event.target.closest("[data-consent]");
    if (!button) return;
    const accepted = button.dataset.consent === "accept";
    const before = readChoice();
    saveChoice(accepted);
    close();
    if (accepted) {
      grant();
    } else {
      if (before && before.analytics) stopAnalytics(gaId);
      document.dispatchEvent(new CustomEvent("consent:declined"));
    }
  });

  banner.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && readChoice() !== null) close();
  });

  root.querySelectorAll("[data-cookie-settings]").forEach((link) => {
    link.hidden = false;
    link.addEventListener("click", () => open(link));
  });

  const choice = readChoice();
  if (choice === null) open();
  else if (choice.analytics) grant();
}
