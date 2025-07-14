#!/bin/bash
# this file not in use for now
set -e

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput


# Start server
gunicorn ai4s_papers_service.wsgi:application --bind 0.0.0.0:${PORT:-8080} 