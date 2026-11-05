// The enquiry forms ([data-contact-form], docs/frontend.md §5): sent with fetch() so errors
// show next to their fields and the thank-you replaces the form, all without a reload. If this
// module doesn't run, the form still works as a normal post.

import { csrfToken, postForm } from "./http.js";

function clearErrors(form) {
  form.querySelectorAll("[data-error-for]").forEach((slot) => {
    slot.textContent = "";
    slot.hidden = true;
  });
  form.querySelectorAll("[aria-invalid]").forEach((field) => field.removeAttribute("aria-invalid"));
  const alert = form.querySelector("[data-form-errors]");
  if (alert) {
    alert.textContent = "";
    alert.hidden = true;
  }
  form.querySelectorAll("[data-form-success]").forEach((note) => note.remove());
}

function showAlert(form, messages) {
  const alert = form.querySelector("[data-form-errors]");
  if (!alert || !messages.length) return null;
  alert.replaceChildren(
    ...messages.map((text) => {
      const p = document.createElement("p");
      p.className = "mb-0";
      p.textContent = text;
      return p;
    }),
  );
  alert.hidden = false;
  return alert;
}

function showErrors(form, errors) {
  const general = [];
  let first = null;
  Object.entries(errors).forEach(([name, messages]) => {
    const slot = form.querySelector(`[data-error-for="${CSS.escape(name)}"]`);
    const field = form.elements.namedItem(name);
    if (name === "__all__" || !slot || !field) {
      general.push(...messages);
      return;
    }
    slot.textContent = messages.join(" ");
    slot.hidden = false;
    field.setAttribute("aria-invalid", "true");
    first = first || field;
  });
  const alert = showAlert(form, general);
  // The alert is announced by its role; with only field errors, move to the first of them.
  if (!alert && first) first.focus();
}

function showSuccess(form, message) {
  const note = document.createElement("div");
  note.className = "form-success";
  note.setAttribute("role", "status");
  note.tabIndex = -1;
  const tick = document.querySelector('template[data-icon="check"]');
  if (tick) note.append(tick.content.cloneNode(true));
  const text = document.createElement("span");
  text.textContent = message || "Thank you, your message has been sent.";
  note.append(text);
  form.replaceWith(note);
  note.focus();
}

function setBusy(form, busy) {
  const button = form.querySelector("[type=submit]");
  form.toggleAttribute("data-busy", busy);
  if (!button) return;
  button.disabled = busy;
  button.setAttribute("aria-busy", String(busy));
}

async function onSubmit(event) {
  const form = event.currentTarget;
  event.preventDefault();
  if (form.hasAttribute("data-busy")) return;
  clearErrors(form);
  setBusy(form, true);
  const result = await postForm(form.action, new FormData(form), { csrf: csrfToken(form) });
  setBusy(form, false);
  if (result.ok) {
    showSuccess(form, result.data.message);
  } else {
    showErrors(form, result.errors);
  }
}

export function initContactForms(root = document) {
  if (!window.fetch || !window.FormData) return; // the normal post still works
  root.querySelectorAll("[data-contact-form]").forEach((form) => {
    form.addEventListener("submit", onSubmit);
  });
}
