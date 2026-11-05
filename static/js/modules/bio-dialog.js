// Team bios: each long [data-bio] is cut to a few lines on its card, with a "Read full bio"
// button that opens the whole bio in a dialog (a native <dialog>: Escape closes it, focus stays
// inside, and returns to the button). Without JavaScript, or without <dialog>, the whole bio
// shows on the card.

function icon(name) {
  const template = document.querySelector(`template[data-icon="${name}"]`);
  return template ? template.content.cloneNode(true) : document.createTextNode("");
}

function buildDialog() {
  const dialog = document.createElement("dialog");
  dialog.className = "bio-dialog";
  dialog.setAttribute("aria-labelledby", "bio-dialog-name");
  dialog.innerHTML = `
    <div class="bio-dialog__inner">
      <button type="button" class="bio-dialog__close" data-bio-close aria-label="Close"></button>
      <div class="bio-dialog__header">
        <img class="bio-dialog__photo" alt="" hidden>
        <div>
          <h2 class="bio-dialog__name" id="bio-dialog-name"></h2>
          <p class="bio-dialog__title"></p>
        </div>
      </div>
      <div class="bio-dialog__bio"></div>
    </div>`;
  dialog.querySelector("[data-bio-close]").append(icon("xmark"));
  dialog.addEventListener("click", (event) => {
    // A click on the backdrop (outside the inner box) closes it too.
    if (event.target === dialog || event.target.closest("[data-bio-close]")) dialog.close();
  });
  document.body.append(dialog);
  return dialog;
}

function openBio(dialog, card, bio, opener) {
  const photo = card.querySelector(".team-card__photo");
  const dialogPhoto = dialog.querySelector(".bio-dialog__photo");
  if (photo) {
    dialogPhoto.src = photo.currentSrc || photo.src;
    dialogPhoto.hidden = false;
  } else {
    dialogPhoto.hidden = true;
  }
  dialog.querySelector(".bio-dialog__name").textContent =
    card.querySelector(".team-card__name")?.textContent || "";
  dialog.querySelector(".bio-dialog__title").textContent =
    card.querySelector(".team-card__title")?.textContent || "";
  dialog.querySelector(".bio-dialog__bio").replaceChildren(
    ...Array.from(bio.cloneNode(true).childNodes),
  );
  dialog.addEventListener("close", () => opener.focus(), { once: true });
  dialog.showModal();
  dialog.querySelector("[data-bio-close]").focus();
}

export function initBioDialogs(root = document) {
  const bios = root.querySelectorAll("[data-bio]");
  if (!bios.length || typeof HTMLDialogElement !== "function") return;
  let dialog = null;

  bios.forEach((bio) => {
    bio.classList.add("is-clamped");
    if (bio.scrollHeight <= bio.clientHeight + 4) {
      bio.classList.remove("is-clamped"); // short enough: no button
      return;
    }
    const card = bio.closest("[data-bio-card]");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "team-card__more";
    button.setAttribute("aria-haspopup", "dialog");
    const name = card?.querySelector(".team-card__name")?.textContent || "";
    button.append(document.createTextNode("Read full bio"));
    const hidden = document.createElement("span");
    hidden.className = "visually-hidden";
    hidden.textContent = name ? ` of ${name}` : "";
    button.append(hidden, icon("arrow-right"));
    button.addEventListener("click", () => {
      dialog = dialog || buildDialog();
      openBio(dialog, card, bio, button);
    });
    bio.after(button);
  });
}
