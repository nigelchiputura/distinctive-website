"""Fixtures for every test under apps/."""

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _empty_cache():
    """Each test starts with no rate-limit counts (config/settings/test.py uses LocMemCache)."""
    cache.clear()
    yield
    cache.clear()
