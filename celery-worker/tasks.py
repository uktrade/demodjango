from config.celery import celery_app
from feedback import utils
from peoplefinder.services.uk_staff_locations import UkStaffLocationService


@celery_app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))  # noqa
