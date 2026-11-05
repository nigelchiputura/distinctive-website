// Runs in <head>, before the page is drawn, so a visitor who chose Light or Dark never sees a
// flash of the other theme. "System" (the default) needs nothing: CSS follows
// prefers-color-scheme. A plain script, not a module, so it runs straight away.
(function () {
  var root = document.documentElement;
  try {
    var choice = window.localStorage.getItem("dcs-theme");
    if (choice === "light" || choice === "dark") root.setAttribute("data-theme", choice);
  } catch (e) {
    // storage blocked: follow the system setting
  }
  root.classList.add("js");
})();
