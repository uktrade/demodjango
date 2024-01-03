import logging

import datetime
import os

import redis
import boto3

from celery_worker.tasks import demodjango_task
from .util import render_connection_info
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
from django.db import connections
from elasticsearch import Elasticsearch


logger = logging.getLogger("django")

def index(request):
    logger.info("Rendering landing page")

    status_output = "".join(
        [
            # server_time_check(),
            # postgres_rds_check(),
            # postgres_aurora_check(),
            sqlite_check(),
            # redis_check(),
            # s3_bucket_check(),
            # opensearch_check(),
            celery_worker_check()
        ]
    )

    return HttpResponse(
        "<!doctype html><html><head><title>DemoDjango</title></head><body>"
        f"{status_output}"
        "</body></html>"
    )


def server_time_check():
    return render_connection_info('Server Time', True, str(datetime.now()))


def postgres_rds_check():
    addon_type = 'PostgreSQL (RDS)'
    try:
        with connections['rds'].cursor() as c:
            c.execute('SELECT version()')
            return render_connection_info(addon_type, True, c.fetchone()[0])
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def postgres_aurora_check():
    addon_type = 'PostgreSQL (Aurora)'
    try:
        with connections['aurora'].cursor() as c:
            c.execute('SELECT version()')
            return render_connection_info(addon_type, True, c.fetchone()[0])
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def sqlite_check():
    addon_type = 'SQLite3'
    try:
        with connections['default'].cursor() as c:
            c.execute('SELECT SQLITE_VERSION()')
            return render_connection_info(addon_type, True, c.fetchone()[0])
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def redis_check():
    addon_type = 'Redis'
    try:
        r = redis.Redis.from_url(f'{settings.REDIS_ENDPOINT}/0')
        return render_connection_info(addon_type, True, r.get('Using').decode())
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def s3_bucket_check():
    addon_type = 'S3 Bucket'
    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.S3_BUCKET_NAME)
        body = bucket.Object('sample_file.txt')
        return render_connection_info(
            addon_type, True, body.get()['Body'].read().decode()
        )
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def opensearch_check():
    addon_type = 'OpenSearch'
    try:
        es = Elasticsearch(f'{settings.OPENSEARCH_ENDPOINT}')
        res = es.get(index="test-index", id=1)
        return render_connection_info(addon_type, True, res['_source']['text'])
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def celery_worker_check():
    addon_type = 'Celery Worker'
    try:
        logger.info("Adding debug task to Celery queue")
        logger.debug(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
        logger.debug(f"CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
        timestamp = datetime.now()
        logger.debug(f"timestamp: {timestamp}")
        # demodjango_task(timestamp)
        demodjango_task.delay(f"{timestamp} delayed")
        return render_connection_info(
            addon_type,
            True,
            "Todo: Part of DBTP-576 Redis disaster recovery"
        )
    except Exception as e:
        logger.info(e)
        return render_connection_info(addon_type, False, str(e))
