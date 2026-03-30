# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (without dev deps) into the system Python
RUN uv sync --frozen --no-dev --no-install-project

# ── Builder stage ──────────────────────────────────────────────────────────────
FROM base AS builder

COPY . .

# Collect static files
RUN SECRET_KEY=build-phase-placeholder \
    DATABASE_URL=sqlite:///tmp/build.sqlite3 \
    DEBUG=False \
    uv run python manage.py collectstatic --noinput

# ── Runtime stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install uv (needed for `uv run`)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy installed packages and app from builder
COPY --from=builder /app /app

# Create non-root user
RUN addgroup --system django && adduser --system --ingroup django django
RUN chown -R django:django /app
USER django

# Expose port
EXPOSE 8000

# Copy entrypoint
COPY --chown=django:django entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uv", "run", "gunicorn", "locallibrary.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
