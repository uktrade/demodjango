from django.http import HttpResponse
from django.conf import settings
from app.models import SampleTable

import redis
import boto3


def index(request):

    if settings.DATABASE_URL:
        DB_TYPE = "Postgres"
    else:
        DB_TYPE = "SQLite"
    db_status = SampleTable.objects.get(sampleid=1).sample_name

    http_page = f"We have a working site<br>{db_status} using a {DB_TYPE} database<br>"

    if settings.REDIS_HOST:
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)
        http_page = http_page + f"Cache using {r.get('Using').decode()}<br>"

    if settings.S3_BUCKET_NAME:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.S3_BUCKET_NAME)
        body = bucket.Object('sample_file.txt')
        http_page = http_page + f"This is {body.get()['Body'].read().decode()}<br>"

    return HttpResponse(http_page)
