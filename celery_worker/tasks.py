import logging

from celery import shared_task

logger = logging.getLogger("django")


@shared_task()
def demodjango_task(timestamp):
    logger.info("Running demodjango_task")
    return f"demodjango_task queued at {timestamp}"


@shared_task()
def demodjango_scheduled_task(timestamp):
    logger.info("Running demodjango_scheduled_task")
    return f"demodjango_scheduled_task queued at {timestamp}"
