"""RateLimitService and BaseController.client_ip."""

import pytest
from django.core.cache.backends.locmem import LocMemCache
from django.test import RequestFactory

from apps.core.controllers.base import BaseController
from apps.core.services.rate_limit_service import RateLimitService


def limiter(limit=2, window=60):
    return RateLimitService("test", limit=limit, window=window, cache=LocMemCache("t", {}))


def test_allows_up_to_the_limit_then_stops():
    rl = limiter(limit=2)
    assert not rl.is_limited("a")
    assert rl.record("a") == 1
    assert rl.record("a") == 2
    assert rl.is_limited("a")
    assert not rl.is_limited("b")  # each visitor counted on their own


def test_an_unknown_visitor_shares_one_bucket():
    rl = limiter(limit=1)
    rl.record("")
    assert rl.key("") == "ratelimit:test:unknown" and rl.is_limited("")


def test_the_count_restarts_when_the_window_ends():
    rl = limiter(limit=1, window=60)
    rl.record("a")
    rl.cache.delete(rl.key("a"))  # what expiry does
    assert not rl.is_limited("a") and rl.record("a") == 1


def test_a_key_that_expires_between_add_and_incr_starts_again():
    class Racy(LocMemCache):
        def add(self, *args, **kwargs):
            return False  # "already there"…

        def incr(self, *args, **kwargs):
            raise ValueError  # …but gone by the time it is counted

    rl = RateLimitService("test", limit=5, window=60, cache=Racy("r", {}))
    assert rl.record("a") == 1 and rl.count("a") == 1


def test_defaults_come_from_settings(settings):
    settings.CONTACT_RATE_LIMIT, settings.CONTACT_RATE_WINDOW = 7, 99
    rl = RateLimitService("contact")
    assert (rl.limit, rl.window) == (7, 99)


@pytest.mark.parametrize(
    ("proxies", "forwarded", "expected"),
    [
        (0, "203.0.113.9", "10.0.0.2"),  # development: the header is ignored
        (1, "203.0.113.9", "203.0.113.9"),  # behind Caddy
        (1, "6.6.6.6, 203.0.113.9", "203.0.113.9"),  # a made-up first entry is ignored
        (1, "", "10.0.0.2"),  # no header
        (1, "not-an-address", "10.0.0.2"),
        (2, "203.0.113.9", "10.0.0.2"),  # fewer entries than proxies
    ],
)
def test_client_ip(settings, proxies, forwarded, expected):
    settings.TRUSTED_PROXY_COUNT = proxies
    meta = {"REMOTE_ADDR": "10.0.0.2"}
    if forwarded:
        meta["HTTP_X_FORWARDED_FOR"] = forwarded
    request = RequestFactory().post("/contact/", **meta)
    assert BaseController.client_ip(request) == expected
