web: python manage.py migrate && python manage.py migrate --database rds && python manage.py migrate --database aurora && python manage.py load_defaults && gunicorn -b 0.0.0.0:$PORT demodjango.wsgi:application
celery-worker: celery -A demodjango.celery worker -l INFO
