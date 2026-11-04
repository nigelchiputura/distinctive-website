# docker/Dockerfile — one file, two variants (docs/deployment.md §2).
# CI and the pushed image: the default REQUIREMENTS=prod.txt.
# docker/docker-compose.yml: REQUIREMENTS=dev.txt (adds pytest, ruff, basedpyright).

# ---- Stage 1: build ----
FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
ARG REQUIREMENTS=prod.txt
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/${REQUIREMENTS} \
    && sha256sum requirements/*.txt > /requirements.sha256
COPY . .
# static/css/main.css is compiled on the dev machine and committed. No Node, no Sass here.
RUN DJANGO_SETTINGS_MODULE=config.settings.prod SECRET_KEY=build-only \
    DATABASE_URL=postgres://build:build@localhost:5432/build \
    python manage.py collectstatic --noinput

# ---- Stage 2: runtime ----
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* && useradd --create-home --uid 1000 appuser
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
# Fingerprint of requirements/ at build time; entrypoint.sh refuses to start on a stale image.
COPY --from=builder /requirements.sha256 /requirements.sha256
COPY docker/entrypoint.sh /entrypoint.sh
# /app/media owned by appuser: an empty named volume mounted there inherits this ownership.
RUN chmod +x /entrypoint.sh && mkdir -p /app/media && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
