"""Database reachability. The only layer that talks to the database (docs/architecture.md §2)."""

from django.db import connection


class HealthRepository:
    def ping(self) -> bool:
        """Run a trivial query; True if the database answered."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
        return row is not None and row[0] == 1
