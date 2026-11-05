"""What the Content Editor group may do (docs/users.md §4).

(app_label, model, actions). A model that doesn't exist yet (its app arrives on a later day) is
skipped; UserService.sync_content_editor_group runs after every `migrate`, so its permissions are
granted as soon as its migration runs. Users, groups and the sign-in tables are never listed.
"""

CONTENT_EDITOR = "Content Editor"

ALL = ("add", "change", "delete", "view")

CONTENT_EDITOR_PERMISSIONS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("core", "sitesettings", ("change", "view")),
    ("pages", "page", ALL),
    ("pages", "pagesection", ALL),
    ("pages", "heroslide", ALL),
    ("pages", "partner", ALL),
    ("pages", "redirect", ALL),
    ("offerings", "service", ALL),
    ("team", "teammember", ALL),
    ("contact", "contactsubmission", ("change", "view")),  # mark handled, resend; never delete
)


def codenames() -> list[tuple[str, str]]:
    """(app_label, codename) pairs, e.g. ("pages", "change_page")."""
    return [
        (app, f"{action}_{model}")
        for app, model, actions in CONTENT_EDITOR_PERMISSIONS
        for action in actions
    ]
