import logging

from celery import shared_task


@shared_task(bind=True)
def demodjango_task(self, timestamp):
    logging.getLogger("django").info("Running demodjango_task")
    print(f"demodjango_task queued at {timestamp}")
    print("Request: {0!r}".format(self.request))
