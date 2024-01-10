web: python manage.py migrate && python manage.py migrate --database rds && python manage.py migrate --database aurora && python manage.py load_defaults && OTEL_PROPAGATORS=xray OTEL_PYTHON_ID_GENERATOR=xray opentelemetry-instrument gunicorn -b 0.0.0.0:$PORT demodjango.wsgi:application
celery-worker: celery --app demodjango.celery worker --task-events --loglevel INFO
