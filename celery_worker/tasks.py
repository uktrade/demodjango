import logging

from celery import shared_task


@shared_task
def demodjango_task(timestamp):
    logging.getLogger("django").info("Running demodjango_task")
    print(f"demodjango_task queued at {timestamp}")
