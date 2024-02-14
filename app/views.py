import json
import logging
import os
from datetime import datetime
from typing import Dict, Callable
from urllib.parse import urlparse

import boto3
import redis
import requests
from django.conf import settings
from django.db import connections
from django.http import HttpResponse
from opensearchpy import OpenSearch
from tenacity import retry, stop_after_delay, RetryError, wait_fixed

from celery_worker.tasks import demodjango_task
from .util import render_connection_info, STATUS_SUCCESS, STATUS_FAIL

logger = logging.getLogger("django")

CELERY = 'celery'
GIT_INFORMATION = 'git_information'
OPENSEARCH = 'opensearch'
POSTGRES_AURORA = 'postgres_aurora'
POSTGRES_RDS = 'postgres_rds'
REDIS = 'redis'
S3 = 's3'
SERVER_TIME = 'server_time'
SQLITE = 'sqlite3'
HTTP_CONNECTION = 'http'

ALL_CHECKS = {
    CELERY: 'Celery Worker',
    GIT_INFORMATION: 'Git information',
    OPENSEARCH: 'OpenSearch',
    POSTGRES_AURORA: 'PostgreSQL (Aurora)',
    POSTGRES_RDS: 'PostgreSQL (RDS)',
    REDIS: 'Redis',
    S3: 'S3 Bucket',
    SERVER_TIME: 'Server Time',
    SQLITE: 'SQLite3',
    HTTP_CONNECTION: 'HTTP Checks',
}


def index(request):
    logger.info("Rendering landing page")
    logger.info({
        "method": request.method,
        "path": request.path,
        "GET": dict(request.GET),
        "POST": dict(request.POST),
        "headers": dict(request.headers),
    })

    status_check_results = [server_time_check(), git_information(), sqlite_check()]

    optional_checks: Dict[str, Callable] = {
        POSTGRES_RDS: postgres_rds_check,
        POSTGRES_AURORA: postgres_aurora_check,
        REDIS: redis_check,
        S3: s3_bucket_check,
        OPENSEARCH: opensearch_check,
        CELERY: celery_worker_check,
        HTTP_CONNECTION: http_check,
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
        "<!doctype html><html><head><title>DemoDjango</title></head><body>"
        f"{''.join(status_check_results)}"
        "</body></html>"
    )


def server_time_check():
    return render_connection_info(ALL_CHECKS[SERVER_TIME], True, str(datetime.utcnow()))


def postgres_rds_check():
    addon_type = ALL_CHECKS[POSTGRES_RDS]
    try:
        with connections['rds'].cursor() as c:
            c.execute('SELECT version()')
            return render_connection_info(addon_type, True, c.fetchone()[0])
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def postgres_aurora_check():
    addon_type = ALL_CHECKS[POSTGRES_AURORA]
    try:
        with connections['aurora'].cursor() as c:
            c.execute('SELECT version()')
            return render_connection_info(addon_type, True, c.fetchone()[0])
    except Exception as e:
        return render_connection_info(addon_type, False, str(e))


def sqlite_check():
    addon_type = ALL_CHECKS[SQLITE]
    try:
        with connections['default'].cursor() as c:
            c.execute('SELECT SQLITE_VERSION()')
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


def git_information():
    git_commit = os.environ.get("GIT_COMMIT", "Unknown")
    git_branch = os.environ.get("GIT_BRANCH", "Unknown")
    git_tag = os.environ.get("GIT_TAG", "Unknown")

    return render_connection_info(ALL_CHECKS[GIT_INFORMATION],
                                  git_commit != "Unknown",
                                  f"Commit: {git_commit}, Branch: {git_branch}, Tag: {git_tag}")


def http_check():
    urls = os.environ.get("HTTP_CHECK_URLS", "https://httpstat.us/200|200|GET").split(",")
    urls = [u for u in urls if u]

    passed = True
    message = ""

    if not urls:
        passed = False
        message = ("No urls provided, set HTTP_CHECK_URLS to a comma separated list of "
                   "URL|STATUS_CODE|METHOD Example: 'http://api.dev.demodjango.internal|200|GET,"
                   "http://api.dev.demodjango.internal/path|403|POST'")

    for url in urls:
        segments = url.split("|")
        url = segments[0]
        url_parsed = urlparse(url)
        status = int(segments[1]) if len(segments) > 1 else 200
        method = segments[2].lower() if len(segments) > 2 else 'get'
        request_success = True

        check_message = f"{method.upper()} {url_parsed.hostname}{url_parsed.path} "

        requester = getattr(requests, method, None)
        if not requester:
            check_message += f"invalid HTTP method {method} "
            request_success = False

        if request_success:
            try:
                r = requester(url)

                if r.status_code != status:
                    check_message += f"response has status code <code>{r.status_code}</code>, but expected <code>{status}</code> "
                    passed = False
                    request_success = False
            except Exception as e:
                passed = False
                request_success = False
                check_message += f"{e} "

        check_message = f'<span style="color: green">{STATUS_SUCCESS}</span> {check_message}' if request_success else f'<span style="color: red">{STATUS_FAIL}</span> {check_message}'
        check_message += "<br>"
        message += check_message

    return render_connection_info(ALL_CHECKS[HTTP_CONNECTION], passed, message)
