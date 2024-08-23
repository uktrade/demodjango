web: scripts/entry.sh
celery-worker: celery --app demodjango.celery worker --task-events --loglevel INFO
celery-beat: celery --app demodjango.celery beat --loglevel INFO
check: python manage.py check
