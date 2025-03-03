web: scripts/entry.sh
celery-worker: ddtrace-run celery --app demodjango.celery worker --task-events --loglevel INFO
celery-beat: ddtrace-run celery --app demodjango.celery beat --loglevel INFO
