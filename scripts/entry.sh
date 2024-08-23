#!/bin/bash -e

# Only run migrations if there is a DB present.
if [[ ! -z "${RDS_POSTGRES_CREDENTIALS}" ]]; then
  echo "Running migrations"
  python manage.py migrate
fi

echo "Loading defaults"
python manage.py load_defaults

echo "Starting web service"
gunicorn -b 0.0.0.0:$PORT demodjango.wsgi:application
