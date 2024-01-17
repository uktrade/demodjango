import os
import tempfile
from pathlib import Path

from celery import Celery
from celery.signals import worker_ready, worker_shutdown

from celery_worker.liveness_probe import LivenessProbe

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demodjango.settings")

READINESS_FILE = Path(f"{tempfile.gettempdir()}/celery_ready")
HEARTBEAT_FILE = Path(f"{tempfile.gettempdir()}/celery_worker_heartbeat")

print(f"Test files: {READINESS_FILE} {HEARTBEAT_FILE}")

celery_app = Celery("demodjango_celery")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()

celery_app.steps["worker"].add(LivenessProbe)


@worker_ready.connect
def worker_ready(**_):
    READINESS_FILE.touch()


@worker_shutdown.connect
def worker_shutdown(**_):
    READINESS_FILE.unlink(missing_ok=True)
