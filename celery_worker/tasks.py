from datetime import datetime
import logging

from celery import shared_task

from app.models import ScheduledTask

logger = logging.getLogger("django")


@shared_task()
def demodjango_task(timestamp):
    logger.info("Running demodjango_task")
    return f"demodjango_task queued at {timestamp}"


@shared_task(bind=True)
def demodjango_scheduled_task(self):
    timestamp = datetime.utcnow()

    task = ScheduledTask()
    task.taskid = self.request.id
    task.timestamp = timestamp
    task.save()

    logger.info(f"Running demodjango_scheduled_task")
    return f"demodjango_scheduled_task queued at {timestamp}"
