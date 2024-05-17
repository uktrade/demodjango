web: python migrate.py && python manage.py load_defaults && gunicorn -b 0.0.0.0:$PORT demodjango.wsgi:application
celery-worker: celery --app demodjango.celery worker --task-events --loglevel INFO
celery-beat: celery --app demodjango.celery beat --loglevel INFO
check: python manage.py check
