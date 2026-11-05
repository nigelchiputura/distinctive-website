// fetch() for our own endpoints (docs/frontend.md §5): the CSRF header, a timeout, and every
// reply turned into the {ok, data, errors} envelope, network failures included, so callers
// handle one shape. `errors.__all__` holds messages that belong to no single field.

const TIMEOUT_MS = 15000;

const MESSAGES = {
  network: "We couldn't reach the server. Please check your connection and try again.",
  timeout: "The server took too long to answer. Please try again.",
  session: "Your session has expired. Please reload the page and try again.",
  server: "Something went wrong on our side. Please try again, or email us instead.",
};

export function csrfToken(form) {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  if (match) return decodeURIComponent(match[1]);
  const field = form ? form.querySelector("input[name=csrfmiddlewaretoken]") : null;
  return field ? field.value : "";
}

function failure(status, message) {
  return { ok: false, status, data: {}, errors: { __all__: [message] } };
}

export async function postForm(url, body, { csrf = "", timeout = TIMEOUT_MS } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(url, {
      method: "POST",
      body,
      credentials: "same-origin",
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrf,
      },
    });
    let json = null;
    try {
      json = await response.json();
    } catch {
      json = null; // not JSON: Django's own 403 or 500 page
    }
    if (json && typeof json.ok === "boolean") {
      return {
        ok: json.ok,
        status: response.status,
        data: json.data || {},
        errors: json.errors || {},
      };
    }
    return failure(response.status, response.status === 403 ? MESSAGES.session : MESSAGES.server);
  } catch (error) {
    return failure(0, error && error.name === "AbortError" ? MESSAGES.timeout : MESSAGES.network);
  } finally {
    clearTimeout(timer);
  }
}
