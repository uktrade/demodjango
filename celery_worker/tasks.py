import logging

from celery import shared_task

logger = logging.getLogger("django")


@shared_task()
def demodjango_task(timestamp):
    logger.info("Running demodjango_task")
    return f"demodjango_task queued at {timestamp}"
