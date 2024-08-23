import logging
import os
from datetime import datetime

import boto3
import redis
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand
from opensearchpy import OpenSearch

from app.models import SampleTable


class Command(BaseCommand):
    def handle(self, *args, **options):
        if os.getenv("IS_API"):
            return

        if settings.RDS_POSTGRES_CREDENTIALS:
            SampleTable.objects.update_or_create(
                sample_id=1, sample_name="Database is connected"
            )

        if settings.REDIS_ENDPOINT:
            r = redis.Redis.from_url(f"{settings.REDIS_ENDPOINT}")
            r.set("test-data", "Test content read from Redis")

        if settings.S3_BUCKET_NAME:
            object_name = os.path.basename("sample_file.txt")
            s3_client = boto3.client("s3")
            try:
                s3_client.upload_file(object_name, settings.S3_BUCKET_NAME, object_name)
            except ClientError as e:
                logging.error(e)

        if settings.OPENSEARCH_ENDPOINT:
            opensearch_client = OpenSearch(f"{settings.OPENSEARCH_ENDPOINT}")

            doc = {
                "author": "author_name",
                "text": "Test content read from OpenSearch.",
                "timestamp": datetime.utcnow(),
            }
            response = opensearch_client.index(index="test-index", id=1, body=doc)
            print(response["result"])
