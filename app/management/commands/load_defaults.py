import redis
import boto3
import logging
from botocore.exceptions import ClientError
import os


from django.core.management.base import BaseCommand

from django.conf import settings
from app.models import SampleTable


class Command(BaseCommand):
    def handle(self, *args, **options):

        # Load single row to db
        SampleTable.objects.update_or_create(sampleid=1, sample_name="DB is connected")

        # Load data into redis
        if settings.REDIS_HOST:
            r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)
            r.set('Using', 'Redis')

        if settings.S3_BUCKET_NAME:
            object_name = os.path.basename("sample_file.txt")
            s3_client = boto3.client('s3')
            try:
                response = s3_client.upload_file(object_name, settings.S3_BUCKET_NAME, object_name)
            except ClientError as e:
                logging.error(e)
