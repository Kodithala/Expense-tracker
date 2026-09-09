#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "==> Running database migrations in live container..."
python manage.py migrate --no-input

echo "==> Ensuring admin superuser exists..."
python manage.py create_admin_user

echo "==> Starting Gunicorn web server..."
exec gunicorn config.wsgi:application
