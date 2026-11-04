#!/bin/sh
# docker/entrypoint.sh — runs before the container's command (docs/deployment.md §2.1).
set -e

# 1. A stale image under the bind mount runs new code against old packages. Refuse to start.
if ! sha256sum -c --quiet /requirements.sha256 >/dev/null 2>&1; then
  echo "ERROR: requirements/ has changed since this image was built."
  echo "Rebuild it:  docker compose -f docker/docker-compose.yml up --build"
  exit 1
fi

# 2. Wait for Postgres (up to 30 seconds), using the app's own DATABASE_URL.
python - <<'PY'
import os, sys, time
import psycopg

url = os.environ.get("DATABASE_URL")
if not url:
    sys.exit("ERROR: DATABASE_URL is not set.")
for attempt in range(30):
    try:
        psycopg.connect(url, connect_timeout=2).close()
        print("Database is ready.")
        break
    except psycopg.OperationalError:
        time.sleep(1)
else:
    sys.exit("ERROR: the database did not answer within 30 seconds.")
PY

# 3. Migrations (this also prints Django's system checks into the logs).
python manage.py migrate --noinput

# 3a. The database cache's table (the enquiry rate limit). Does nothing if it is already there.
python manage.py createcachetable

# 4. First deploy only: load the old site's content (the command arrives on Day 5).
if [ "$SEED_SITE_CONTENT" = "true" ]; then
  python manage.py seed_site_content
fi

# 5. Hand over to the container's command: gunicorn in the image, runserver under compose.
exec "$@"
