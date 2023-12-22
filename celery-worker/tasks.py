from config.celery import celery_app


@celery_app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))