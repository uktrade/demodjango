import os

from celery import Celery
from dbt_copilot_python.celery_health_check import healthcheck

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demodjango.settings")

celery_app = Celery("demodjango_celery")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()

celery_app = healthcheck.setup(celery_app)

# celery_app.conf.beat_schedule = {
#     "schedule-demodjango-task": {
#         "task": "celery_worker.tasks.demodjango_scheduled_task",
#         "schedule": crontab(hour=0, minute=1),
#     },
# }
