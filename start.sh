#!/bin/bash

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput


# Start server
gunicorn ai4s_papers_service.wsgi:application --bind 0.0.0.0:${PORT:-8080} 