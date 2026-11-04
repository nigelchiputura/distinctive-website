"""HealthService with fake repositories: no database needed."""

from apps.core.services.health_service import HealthService


class FakeRepo:
    def __init__(self, result=True, error: Exception | None = None):
        self.result = result
        self.error = error

    def ping(self):
        if self.error:
            raise self.error
        return self.result


def test_database_answering_is_ok():
    service = HealthService(repo=FakeRepo(result=True))
    status = service.check()
    assert status == {"db": "ok"}
    assert service.is_healthy(status)


def test_database_not_answering_is_error():
    service = HealthService(repo=FakeRepo(result=False))
    status = service.check()
    assert status == {"db": "error"}
    assert not service.is_healthy(status)


def test_database_exception_is_reported_not_raised(caplog):
    service = HealthService(repo=FakeRepo(error=RuntimeError("connection refused")))
    assert service.check() == {"db": "error"}
    assert "database unreachable" in caplog.text
