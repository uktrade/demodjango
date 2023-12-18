import logging

import redis
import boto3
from .util import render_connection_info
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
from django.db import connections
from elasticsearch import Elasticsearch


def index(request):
    logging.getLogger("django").info("Rendering landing page")

    status_output = render_connection_info('Server Time', True, str(datetime.now()))

    try:
        with connections['rds'].cursor() as c:
            c.execute('SELECT version()')
            status_output += render_connection_info('PostgreSQL (RDS)', True, c.fetchone()[0])
    except Exception as e:
        status_output += render_connection_info('PostgreSQL (RDS)', False, str(e))

    try:
        with connections['aurora'].cursor() as c:
            c.execute('SELECT version()')
            status_output += render_connection_info('PostgreSQL (Aurora)', True, c.fetchone()[0])
    except Exception as e:
        status_output += render_connection_info('PostgreSQL (Aurora)', False, str(e))

    try:
        with connections['default'].cursor() as c:
            c.execute('SELECT SQLITE_VERSION()')
            status_output += render_connection_info('SQLite3', True, c.fetchone()[0])
    except Exception as e:
        status_output += render_connection_info('SQLite3', False, str(e))

    try:
        r = redis.Redis.from_url(f'{settings.REDIS_ENDPOINT}/0')
        status_output += render_connection_info('Redis', True, r.get('Using').decode())
    except Exception as e:
        status_output += render_connection_info('Redis', False, str(e))

    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.S3_BUCKET_NAME)
        body = bucket.Object('sample_file.txt')
        status_output += render_connection_info('S3 Bucket', True, body.get()['Body'].read().decode())
    except Exception as e:
        status_output += render_connection_info('S3 Bucket', False, str(e))

    try:
        es = Elasticsearch(f'{settings.OPENSEARCH_ENDPOINT}')
        res = es.get(index="test-index", id=1)
        status_output += render_connection_info('OpenSearch', True, res['_source']['text'])
    except Exception as e:
        status_output += render_connection_info('OpenSearch', False, str(e))

    return HttpResponse("<!doctype html><html><head><title>DemoDjango</title></head><body>"
                        f"{status_output}"
                        "</body></html>")
