import redis
import boto3
import logging
import os

from botocore.exceptions import ClientError
from datetime import datetime
from opensearchpy import OpenSearch
from django.core.management.base import BaseCommand
from django.conf import settings
from app.models import SampleTable


class Command(BaseCommand):
    def handle(self, *args, **options):

        SampleTable.objects.update_or_create(sampleid=1, sample_name="Database is connected")

        if settings.REDIS_ENDPOINT:
            r = redis.Redis.from_url(f'{settings.REDIS_ENDPOINT}')
            r.set('test-data', 'Test content read from Redis')

        if settings.S3_BUCKET_NAME:
            object_name = os.path.basename("sample_file.txt")
            s3_client = boto3.client('s3')
            try:
                s3_client.upload_file(object_name, settings.S3_BUCKET_NAME, object_name)
            except ClientError as e:
                logging.error(e)

        if settings.OPENSEARCH_ENDPOINT:
            opensearch_client = OpenSearch(f'{settings.OPENSEARCH_ENDPOINT}')

            doc = {
                'author': 'author_name',
                'text': 'Test content read from OpenSearch.',
                'timestamp': datetime.utcnow(),
            }
            response = opensearch_client.index(index="test-index", id=1, body=doc)
            print(response['result'])
