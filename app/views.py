import json
import logging
import os
from datetime import datetime
from typing import Dict, Callable

import boto3
import redis
from django.conf import settings
from django.db import connections
from django.http import HttpResponse
from opensearchpy import OpenSearch
from tenacity import retry, stop_after_delay, RetryError, wait_fixed

from celery_worker.tasks import demodjango_task
from .check.check_http import HTTPCheck

from .util import render_connection_info

logger = logging.getLogger("django")

CELERY = 'celery'
BEAT = 'beat'
GIT_INFORMATION = 'git_information'
HTTP_CONNECTION = 'http'
OPENSEARCH = 'opensearch'
POSTGRES_RDS = 'postgres_rds'
PRIVATE_SUBMODULE = 'private_submodule'
READ_WRITE = 'read_write'
REDIS = 'redis'
S3 = 's3'
SERVER_TIME = 'server_time'

ALL_CHECKS = {
    BEAT: 'Celery Beat',
    CELERY: 'Celery Worker',
    GIT_INFORMATION: 'Git information',
    HTTP_CONNECTION: 'HTTP Checks',
    OPENSEARCH: 'OpenSearch',
    POSTGRES_RDS: 'PostgreSQL (RDS)',
    PRIVATE_SUBMODULE: 'Private submodule',
    READ_WRITE: 'Filesystem read/write',
    REDIS: 'Redis',
    S3: 'S3 Bucket',
    SERVER_TIME: 'Server Time',
}

RDS_POSTGRES_CREDENTIALS = os.environ.get("RDS_POSTGRES_CREDENTIALS", "")


def index(request):
    logger.info("Rendering landing page")
    logger.info({
        "method": request.method,
        "path": request.path,
        "GET": dict(request.GET),
        "POST": dict(request.POST),
        "headers": dict(request.headers),
    })

    status_check_results = [server_time_check(), git_information()]

    optional_checks: Dict[str, Callable] = {
        POSTGRES_RDS: postgres_rds_check,
        READ_WRITE: read_write_check,
        REDIS: redis_check,
        S3: s3_bucket_check,
        OPENSEARCH: opensearch_check,
        CELERY: celery_worker_check,
        BEAT: celery_beat_check,
        HTTP_CONNECTION: http_check,
        PRIVATE_SUBMODULE: private_submodule_check,
    }

    if settings.ACTIVE_CHECKS:
        for name, check in optional_checks.items():
            if name in settings.ACTIVE_CHECKS:
                status_check_results.append(check())
    else:
        status_check_results += [f() for f in optional_checks.values()]

    logger.info(f"Landing page checks completed: "
                f"{settings.ACTIVE_CHECKS if settings.ACTIVE_CHECKS else 'all'}")

    return HttpResponse(
        "<!doctype html><html><head>"
        "<title>DemoDjango</title>"
        "</head><body>"
        f"{''.join(status_check_results)}"
        "</body></html>"
    )


def server_time_check():
    return render_connection_info(ALL_CHECKS[SERVER_TIME], True, str(datetime.utcnow()))


def postgres_rds_check():
    addon_type = ALL_CHECKS[POSTGRES_RDS]
    try:
        if not RDS_POSTGRES_CREDENTIALS:
            raise Exception("No RDS database")

        with connections['default'].cursor() as c:
            c.execute('SELECT version()')
            return render_connection_info(addon_type, True, c.fetchone()[0])
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def redis_check():
    addon_type = ALL_CHECKS[REDIS]
    try:
        r = redis.Redis.from_url(f'{settings.REDIS_ENDPOINT}')
        return render_connection_info(addon_type, True, r.get('test-data').decode())
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def s3_bucket_check():
    addon_type = ALL_CHECKS[S3]
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
    addon_type = ALL_CHECKS[OPENSEARCH]
    get_result_timeout = 5

    @retry(stop=stop_after_delay(get_result_timeout), wait=wait_fixed(1))
    def read_content_from_opensearch():
        opensearch_client = OpenSearch(f'{settings.OPENSEARCH_ENDPOINT}')
        results = opensearch_client.get(index="test-index", id=1)
        return results

    try:
        results = read_content_from_opensearch()
        return render_connection_info(addon_type, True, results['_source']['text'])
    except RetryError:
        connection_info = f"Unable to read content from {addon_type} within {get_result_timeout} seconds"
        logger.error(connection_info)
        return render_connection_info(addon_type, False, connection_info)
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def celery_worker_check():
    from demodjango import celery_app

    addon_type = ALL_CHECKS[CELERY]
    get_result_timeout = 2

    @retry(stop=stop_after_delay(get_result_timeout), wait=wait_fixed(1))
    def get_result_from_celery_backend():
        logger.info("Getting result from Celery backend")
        backend_result = json.loads(celery_app.backend.get(f"celery-task-meta-{task_id}"))
        logger.debug("backend_result")
        logger.debug(backend_result)
        if backend_result['status'] != "SUCCESS":
            raise Exception
        return backend_result

    try:
        timestamp = datetime.utcnow()
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


def celery_beat_check():
    from .models import ScheduledTask
    addon_type = ALL_CHECKS[BEAT]

    try:
        if not RDS_POSTGRES_CREDENTIALS:
            raise Exception("Database not found")

        latest_task = ScheduledTask.objects.all().order_by('-timestamp').first()
        connection_info = f"Latest task scheduled with task_id {latest_task.taskid} at {latest_task.timestamp}"
        return render_connection_info(addon_type, True, connection_info)
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def read_write_check():
    import tempfile
    addon_type = ALL_CHECKS[READ_WRITE]
    timestamp = datetime.now()  # ensures no stale file is present

    try:
        # create a temporary file
        temp = tempfile.NamedTemporaryFile()

        # write into temporary file
        with open(temp.name, 'w') as f:
            f.write(str(timestamp))

        # read from temporary file
        with open(temp.name, 'r') as f:
            from_file_timestamp = f.read()

        # delete temporary file
        temp.close()

        read_write_status = f"Read/write successfully completed at {from_file_timestamp}"
        return render_connection_info(addon_type, True, read_write_status)
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def git_information():
    git_commit = os.environ.get("GIT_COMMIT", "Unknown")
    git_branch = os.environ.get("GIT_BRANCH", "Unknown")
    git_tag = os.environ.get("GIT_TAG", "Unknown")

    return render_connection_info(ALL_CHECKS[GIT_INFORMATION],
                                  git_commit != "Unknown",
                                  f"Commit: {git_commit}, Branch: {git_branch}, Tag: {git_tag}")


def http_check():
    urls = os.environ.get("HTTP_CHECK_URLS", "https://httpstat.us/200|200|GET")

    check = HTTPCheck(urls)
    check.execute()

    return render_connection_info(ALL_CHECKS[HTTP_CONNECTION],
                                  check.success,
                                  "".join([c.render() for c in check.report]))


def private_submodule_check():
    file_path = "platform-demo-private/sample.txt"
    success = False
    connection_info = f"Failed to read file from private submodule at path: {file_path}"
    
    if os.path.exists(file_path):
        pass
    
    with open(file_path, 'r') as file:
        content = file.read()
        if 'lorem ipsum' in content.lower():
            success = True
            connection_info = f"Successfully built sample.txt file in private submodule at: {file_path}"
        
        
    return render_connection_info(ALL_CHECKS[PRIVATE_SUBMODULE], success, connection_info)
