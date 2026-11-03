"""The custom user model: email login, and created before anything that depends on it."""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


def test_custom_user_model_is_active():
    assert get_user_model()._meta.label == "users.User"
    assert get_user_model().USERNAME_FIELD == "email"


@pytest.mark.django_db
def test_email_is_lower_cased_and_trimmed():
    user = get_user_model().objects.create_user(
        username="tendai", email="  Tendai.M@Distinctive.CO.ZW ", password="x" * 12
    )
    user.refresh_from_db()
    assert user.email == "tendai.m@distinctive.co.zw"


@pytest.mark.django_db
def test_users_migration_runs_before_admin_and_auth_dependants():
    """AUTH_USER_MODEL must exist before admin.0001 (docs/users.md §1)."""
    executor = MigrationExecutor(connection)
    plan = [
        m.app_label + "." + m.name
        for m, _ in executor.migration_plan(executor.loader.graph.leaf_nodes(), clean_start=True)
    ]
    assert plan.index("users.0001_initial") < plan.index("admin.0001_initial")
