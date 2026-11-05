from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _sync_content_editor_group(sender, **kwargs) -> None:
    """After every app's migrations: grant the Content Editor group any permissions that now
    exist (a later day's models get theirs the moment their migration runs)."""
    from apps.users.services.user_service import UserService

    UserService().sync_content_editor_group()


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    label = "users"
    verbose_name = "Users"

    def ready(self) -> None:
        post_migrate.connect(_sync_content_editor_group, dispatch_uid="users.sync_content_editor")
