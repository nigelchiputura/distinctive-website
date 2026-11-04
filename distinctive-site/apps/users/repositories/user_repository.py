"""Users, groups and permissions: the only place the users app touches the ORM."""

from typing import Any

from django.contrib.auth.models import Group, Permission

from apps.core.repositories.base import BaseRepository
from apps.users.models import User


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return User._default_manager.filter(email__iexact=email.strip()).first()

    def create_user(self, email: str, **fields: Any) -> User:
        """Through the manager, so the username is filled in from the email."""
        return User.objects.create_user(email, **fields)

    def set_active(self, user: User, active: bool) -> User:
        user.is_active = active
        user.save(update_fields=["is_active"])
        return user

    def add_to_group(self, user: User, group_name: str) -> None:
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

    def group_exists(self, name: str) -> bool:
        return Group.objects.filter(name=name).exists()

    def set_group_permissions(self, group_name: str, pairs: list[tuple[str, str]]) -> list[str]:
        """Give the group exactly the listed permissions that exist; return the ones granted."""
        group, _ = Group.objects.get_or_create(name=group_name)
        found = [
            perm
            for app_label, codename in pairs
            if (
                perm := Permission.objects.filter(
                    content_type__app_label=app_label, codename=codename
                ).first()
            )
        ]
        group.permissions.set(found)
        return sorted(f"{p.content_type.app_label}.{p.codename}" for p in found)
