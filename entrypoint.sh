#!/bin/sh
set -e

echo "==> Waiting for database..."
# Simple wait loop - tries to connect before starting
until uv run python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locallibrary.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
print('Database ready!')
" 2>/dev/null; do
  echo "Database not ready yet - sleeping 1s"
  sleep 1
done

echo "==> Running migrations..."
uv run python manage.py migrate --noinput

echo "==> Starting application..."
exec "$@"
