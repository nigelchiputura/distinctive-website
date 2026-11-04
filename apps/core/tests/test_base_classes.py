"""BaseRepository and the model mixins, on a throwaway model created only for these tests."""

import pytest
from django.db import connection, models
from django.test.utils import isolate_apps

from apps.core.exceptions import NotFoundError
from apps.core.models import BaseModel, OrderableMixin, PublishableMixin, SluggedMixin
from apps.core.repositories.base import BaseRepository
from apps.core.services.base import BaseService

pytestmark = pytest.mark.django_db


@pytest.fixture
def article_model():
    """A model using every mixin, with its table created for the test and dropped after."""
    with isolate_apps("apps.core"):

        class Article(BaseModel, PublishableMixin, OrderableMixin, SluggedMixin):
            title = models.CharField(max_length=100)

            class Meta(OrderableMixin.Meta):
                app_label = "core"

        with connection.schema_editor() as editor:
            editor.create_model(Article)
        yield Article
        with connection.schema_editor() as editor:
            editor.delete_model(Article)


@pytest.fixture
def repo(article_model):
    class ArticleRepository(BaseRepository):
        model = article_model

    return ArticleRepository()


def test_create_get_update_delete(repo):
    a = repo.create(title="Hello")
    assert repo.get(pk=a.pk).title == "Hello"
    repo.update(a, title="Changed")
    assert repo.get(pk=a.pk).title == "Changed"
    repo.delete(a)
    assert repo.get_or_none(pk=a.pk) is None


def test_get_raises_not_found(repo):
    with pytest.raises(NotFoundError):
        repo.get(pk=999)


def test_list_exists_count(repo):
    repo.create(title="One")
    repo.create(title="Two")
    assert repo.count() == 2
    assert repo.exists(title="One")
    assert not repo.exists(title="Three")
    assert [a.title for a in repo.list(title__startswith="T")] == ["Two"]


def test_published_hides_unpublished(repo):
    repo.create(title="Live")
    repo.create(title="Draft", is_published=False)
    assert [a.title for a in repo.published()] == ["Live"]


def test_published_needs_a_publishable_model():
    from apps.core.repositories.site_settings_repository import SiteSettingsRepository

    with pytest.raises(TypeError):
        SiteSettingsRepository().published()


def test_published_at_is_set_once(repo):
    a = repo.create(title="Live")
    first = a.published_at
    assert first is not None
    repo.update(a, title="Edited")
    assert repo.get(pk=a.pk).published_at == first
    draft = repo.create(title="Draft", is_published=False)
    assert draft.published_at is None


def test_default_ordering_by_sort_order_then_age(repo):
    repo.create(title="C", sort_order=2)
    repo.create(title="A", sort_order=1)
    repo.create(title="B", sort_order=1)
    assert [a.title for a in repo.list()] == ["A", "B", "C"]


def test_slugs_are_unique_and_stable(repo):
    first = repo.create(title="About Us")
    second = repo.create(title="About Us")
    assert (first.slug, second.slug) == ("about-us", "about-us-2")
    repo.update(first, title="Renamed")
    assert repo.get(pk=first.pk).slug == "about-us"  # links already out there keep working


def test_slug_for_an_empty_title(repo):
    assert repo.create(title="!!!").slug == "item"


def test_get_or_raise():
    assert BaseService.get_or_raise("x") == "x"
    with pytest.raises(NotFoundError, match="Nope"):
        BaseService.get_or_raise(None, "Nope")
