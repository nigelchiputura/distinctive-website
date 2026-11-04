"""BaseRepository: the generic queries every repository gets (docs/architecture.md §4).

Repositories are the only layer that calls `Model.objects`. Subclasses set `model`.
"""

from typing import Any, ClassVar

from django.db import models

from apps.core.exceptions import NotFoundError


class BaseRepository[T: models.Model]:
    model: ClassVar[type[models.Model]]

    def _manager(self) -> models.Manager[Any]:
        return self.model._default_manager

    def get(self, **lookup: Any) -> T:
        """The one matching row; NotFoundError if there's none."""
        obj = self.get_or_none(**lookup)
        if obj is None:
            raise NotFoundError(f"No {self.model._meta.verbose_name} matches {lookup}.")
        return obj

    def get_or_none(self, **lookup: Any) -> T | None:
        return self._manager().filter(**lookup).first()

    def list(self, **filters: Any) -> models.QuerySet[Any]:
        return self._manager().filter(**filters)

    def create(self, **data: Any) -> T:
        return self._manager().create(**data)

    def update(self, obj: T, **data: Any) -> T:
        for field, value in data.items():
            setattr(obj, field, value)
        obj.save()
        return obj

    def delete(self, obj: T) -> None:
        obj.delete()

    def exists(self, **filters: Any) -> bool:
        return self._manager().filter(**filters).exists()

    def count(self, **filters: Any) -> int:
        return self._manager().filter(**filters).count()

    def published(self, **filters: Any) -> models.QuerySet[Any]:
        """Only rows an editor has published. For models with PublishableMixin."""
        if not any(f.name == "is_published" for f in self.model._meta.get_fields()):
            raise TypeError(f"{self.model.__name__} has no is_published field.")
        return self._manager().filter(is_published=True, **filters)
