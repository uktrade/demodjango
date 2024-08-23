import logging
from datetime import datetime

from celery import shared_task

logger = logging.getLogger("django")


@shared_task()
def demodjango_task(timestamp):
    logger.info("Running demodjango_task")
    return f"demodjango_task queued at {timestamp}"


@shared_task(bind=True)
def demodjango_scheduled_task(self):
    from app.models import ScheduledTask

    timestamp = datetime.utcnow()

    task = ScheduledTask()
    task.taskid = self.request.id
    task.timestamp = timestamp
    task.save()

    logger.info(f"Running demodjango_scheduled_task")
    return f"demodjango_scheduled_task queued at {timestamp}"
