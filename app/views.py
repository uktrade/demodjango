import datetime
import json
import logging
from datetime import datetime

import boto3
import redis
from django.conf import settings
from django.db import connections
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from tenacity import retry, stop_after_delay, RetryError

from celery_worker.tasks import demodjango_task
from demodjango import celery_app
from .util import render_connection_info

logger = logging.getLogger("django")

def index(request):
    logger.info("Rendering landing page")

    status_output = "".join(
        [
            server_time_check(),
            postgres_rds_check(),
            postgres_aurora_check(),
            sqlite_check(),
            redis_check(),
            s3_bucket_check(),
            opensearch_check(),
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
        r = redis.Redis.from_url(f'{settings.REDIS_ENDPOINT}')
        return render_connection_info(addon_type, True, r.get('test-data').decode())
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
    get_result_timeout = 2

    @retry(stop=stop_after_delay(get_result_timeout))
    def get_result_from_celery_backend():
        logger.info("Getting result from Celery backend")
        backend_result = json.loads(celery_app.backend.get(f"celery-task-meta-{task_id}"))
        logger.debug("backend_result")
        logger.debug(backend_result)
        if backend_result['status'] != "SUCCESS":
            raise Exception
        return backend_result

    try:
        timestamp = datetime.now()
        logger.info("Adding debug task to Celery queue")
        task_id = str(demodjango_task.delay(f"{timestamp}"))
        backend_result = get_result_from_celery_backend()
        connection_info = f"{backend_result['result']} with task_id {task_id} was processed at {backend_result['date_done']} with status {backend_result['status']}"
        return render_connection_info(addon_type, True, connection_info)
    except RetryError:
        connection_info = f"task_id {task_id} was not processed within {get_result_timeout} seconds"
        logger.error(connection_info)
        return render_connection_info(addon_type, False, connection_info)
    except Exception as e:
        logger.error(e)
        return render_connection_info(addon_type, False, str(e))
