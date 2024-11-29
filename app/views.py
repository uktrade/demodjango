import base64
import json
import logging
import os
from datetime import datetime
from typing import Callable
from typing import Dict

import boto3
import redis
import requests
from authbroker_client.utils import TOKEN_SESSION_KEY
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connections
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from opensearchpy import OpenSearch
from tenacity import RetryError
from tenacity import retry
from tenacity import stop_after_delay
from tenacity import wait_fixed

from celery_worker.tasks import demodjango_task

from .check.check_http import HTTPCheck
from .util import Check, CheckResult
from .util import render_connection_info

logger = logging.getLogger("django")

def dummy():
    return "OK"

class PostgresRdsCheck(Check):
    def __call__(self):
        try:
            if not RDS_POSTGRES_CREDENTIALS:
                raise Exception("No RDS database")

            with connections["default"].cursor() as c:
                c.execute("SELECT version()")
                return [CheckResult(self.type, self.description, True, c.fetchone()[0])]
        except Exception as e:
            return [CheckResult(self.type, self.description, False, str(e))]


CELERY = Check("celery", "Celery Worker", dummy, True)
BEAT = Check("beat", "Celery Worker", dummy, True)
GIT_INFORMATION = Check("git_information", "Git information", dummy, True)
HTTP_CONNECTION = Check("http", "HTTP Checks", dummy, True)
OPENSEARCH = Check("opensearch", "OpenSearch", dummy, True)
PRIVATE_SUBMODULE = Check("private_submodule", "Private submodule", dummy, True)
READ_WRITE = Check("read_write", "Filesystem read/write", dummy, True)
REDIS = Check("redis", "Redis", dummy, True)
# TODO change optional flag to mandatory and invert values
SERVER_TIME = Check("server_time", "Server Time", dummy) 
S3 = Check("s3", dummy, True)
S3_ADDITIONAL = Check("s3_additional", "S3 Additional Bucket", dummy, True)
S3_STATIC = Check("s3_static", "S3 Bucket for static assets", dummy, True)
S3_CROSS_ENVIRONMENT = Check("s3_cross_environment", "Cross environment S3 Buckets", dummy, True)

MANDATORY_CHECKS = [
    GIT_INFORMATION,
    SERVER_TIME,
]

OPTIONAL_CHECKS = [
    BEAT,
    CELERY,
    GIT_INFORMATION,
    HTTP_CONNECTION,
    OPENSEARCH,
    PostgresRdsCheck("postgres_rds",  "PostgreSQL (RDS)", dummy, True),
    PRIVATE_SUBMODULE,
    READ_WRITE,
    REDIS,
    S3,
    S3_ADDITIONAL,
    S3_STATIC,
    S3_CROSS_ENVIRONMENT,
    SERVER_TIME,
]

RDS_POSTGRES_CREDENTIALS = os.environ.get("RDS_POSTGRES_CREDENTIALS", "")


def index(request):
    logger.info("Rendering landing page")
    logger.info(
        {
            "method": request.method,
            "path": request.path,
            "GET": dict(request.GET),
            "POST": dict(request.POST),
            "headers": dict(request.headers),
        }
    )

    active_checks = MANDATORY_CHECKS + [check for check in OPTIONAL_CHECKS if settings.ACTIVE_CHECKS and check.type in settings.ACTIVE_CHECKS]

    results = []
    
    for check in active_checks:
        results.extend(check())

    logger.info(
        f"Landing page checks completed: "
        f"{settings.ACTIVE_CHECKS if settings.ACTIVE_CHECKS else 'all'}"
    )

    if request.GET.get("json", None) == "true":
        results = [result.to_dict() for result in results]
        return JsonResponse({"check_results": results}, status=200)
    else:
        results = [render_connection_info(result) for result in results]
        return HttpResponse(
            "<!doctype html><html><head>"
            "<title>DemoDjango</title>"
            "</head><body>"
            f"{''.join(results)}"
            "</body></html>"
        )


def server_time_check():
    return [
        CheckResult(None, None, True, str(datetime.utcnow()), SERVER_TIME)
    ]





def redis_check():
    try:
        r = redis.Redis.from_url(f"{settings.REDIS_ENDPOINT}")
        return [CheckResult(None, None, True, r.get("test-data").decode(), REDIS)]
    except Exception as e:
        return [CheckResult(None, None, False, str(e), REDIS)]


def _s3_bucket_check(check, bucket_name):
    try:
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        body = bucket.Object("sample_file.txt")
        return CheckResult(
            None,
            None,
            True,
            f'{body.get()["Body"].read().decode()}Bucket: {bucket_name}',
            check
        )
    except Exception as e:
        return CheckResult(None, None, False, str(e), check)


def s3_bucket_check():
    return [_s3_bucket_check(S3, settings.S3_BUCKET_NAME)]


def s3_cross_environment_bucket_check():
    buckets = settings.S3_CROSS_ENVIRONMENT_BUCKET_NAMES.split(",")
    check_results = []
    for bucket in buckets:
        if bucket.strip():
            check = Check(S3_CROSS_ENVIRONMENT.type, f"{S3_CROSS_ENVIRONMENT.description} ({bucket})", dummy, True)
            check_results.append(_s3_bucket_check(check, bucket))
    return check_results


def s3_additional_bucket_check():
    return [
        _s3_bucket_check(S3_ADDITIONAL, settings.ADDITIONAL_S3_BUCKET_NAME
        )
    ]


def s3_static_bucket_check():
    try:
        response = requests.get(f"{settings.STATIC_S3_ENDPOINT}/test.html")
        if response.status_code == 200:
            parsed_html = BeautifulSoup(response.text, "html.parser")
            test_text = parsed_html.body.find("p").text
            return [CheckResult(None, None, True, test_text, S3_STATIC)]

        raise Exception(
            f"Failed to get static asset with status code: {response.status_code}"
        )
    except Exception as e:
        return [CheckResult(None, None, False, str(e), S3_STATIC)]


def opensearch_check():
    get_result_timeout = 5

    @retry(stop=stop_after_delay(get_result_timeout), wait=wait_fixed(1))
    def read_content_from_opensearch():
        opensearch_client = OpenSearch(f"{settings.OPENSEARCH_ENDPOINT}")
        results = opensearch_client.get(index="test-index", id=1)
        return results

    try:
        results = read_content_from_opensearch()
        return [CheckResult(None, None, True, results["_source"]["text"], OPENSEARCH)]
    except RetryError:
        connection_info = f"Unable to read content from {OPENSEARCH.description} within {get_result_timeout} seconds"
        logger.error(connection_info)
        return [CheckResult(None, None, False, connection_info, OPENSEARCH)]
    except Exception as e:
        return [CheckResult(None, None, False, str(e), OPENSEARCH)]


def celery_worker_check():
    from demodjango import celery_app

    get_result_timeout = 2

    @retry(stop=stop_after_delay(get_result_timeout), wait=wait_fixed(1))
    def get_result_from_celery_backend():
        logger.info("Getting result from Celery backend")
        backend_result = json.loads(
            celery_app.backend.get(f"celery-task-meta-{task_id}")
        )
        logger.debug("backend_result")
        logger.debug(backend_result)
        if backend_result["status"] != "SUCCESS":
            raise Exception
        return backend_result

    try:
        timestamp = datetime.utcnow()
        logger.info("Adding debug task to Celery queue")
        task_id = str(demodjango_task.delay(f"{timestamp}"))
        backend_result = get_result_from_celery_backend()
        connection_info = f"{backend_result['result']} with task_id {task_id} was processed at {backend_result['date_done']} with status {backend_result['status']}"
        return [CheckResult(None, None, True, connection_info, CELERY)]
    except RetryError:
        connection_info = (
            f"task_id {task_id} was not processed within {get_result_timeout} seconds"
        )
        logger.error(connection_info)
        return [CheckResult(None, None, False, connection_info, CELERY)]
    except Exception as e:
        logger.error(e)
        return [CheckResult(None, None, False, str(e), CELERY)]


def celery_beat_check():
    from .models import ScheduledTask

    try:
        if not RDS_POSTGRES_CREDENTIALS:
            raise Exception("Database not found")

        latest_task = ScheduledTask.objects.all().order_by("-timestamp").first()
        connection_info = f"Latest task scheduled with task_id {latest_task.taskid} at {latest_task.timestamp}"
        return [CheckResult(None, None, True, connection_info, BEAT)]
    except Exception as e:
        return [CheckResult(None, None, False, str(e), BEAT)]


def read_write_check():
    import tempfile

    timestamp = datetime.now()  # ensures no stale file is present

    try:
        # create a temporary file
        temp = tempfile.NamedTemporaryFile()

        # write into temporary file
        with open(temp.name, "w") as f:
            f.write(str(timestamp))

        # read from temporary file
        with open(temp.name, "r") as f:
            from_file_timestamp = f.read()

        # delete temporary file
        temp.close()

        read_write_status = (
            f"Read/write successfully completed at {from_file_timestamp}"
        )
        return [CheckResult(None, None, True, read_write_status, READ_WRITE)]
    except Exception as e:
        return [CheckResult(None, None, False, str(e), READ_WRITE)]


def git_information():
    git_commit = os.environ.get("GIT_COMMIT", "Unknown")
    git_branch = os.environ.get("GIT_BRANCH", "Unknown")
    git_tag = os.environ.get("GIT_TAG", "Unknown")

    return [
        CheckResult(
            None,
            None,
            git_commit != "Unknown",
            f"Commit: {git_commit}, Branch: {git_branch}, Tag: {git_tag}",
            GIT_INFORMATION
        )
    ]


def http_check():
    urls = os.environ.get("HTTP_CHECK_URLS", "https://httpstat.us/200|200|GET")

    check = HTTPCheck(urls)
    check.execute()

    return [
        CheckResult(
            None,
            None,
            check.success,
            "".join([c.render() for c in check.report]),
            HTTP_CONNECTION
        )
    ]


def private_submodule_check():
    file_path = "platform-demo-private/sample.txt"
    success = False
    connection_info = f"Failed to read file from private submodule at path: {file_path}"

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            content = file.read()
            if "lorem ipsum" in content.lower():
                success = True
                connection_info = f"Successfully built sample.txt file in private submodule at: {file_path}"

    return [
        CheckResult(
            None, None, success, connection_info, PRIVATE_SUBMODULE
        )
    ]


def api(request):
    response_data = {"message": "Success", "timestamp": datetime.now().isoformat()}

    return JsonResponse(response_data)


def test_web(request):
    api_url = reverse("api")
    full_api_url = request.build_absolute_uri(api_url)
    web_url = full_api_url.replace(".api", "")
    response = requests.get(web_url)

    if response.status_code == 200:
        return JsonResponse(
            {"message": f"API reached web service at {web_url}"}, status=200
        )
    else:
        return JsonResponse(
            {"message": f"API failed to reach web service at {web_url}"},
            status=response.status_code,
        )


def test_api(request):
    index_url = reverse("index")
    logger.info({"index_url": index_url})
    full_index_url = request.build_absolute_uri(index_url)
    logger.info({"full_index_url": full_index_url})
    api_url = full_index_url.replace("web.", "api.")
    logger.info({"api_url": api_url})
    response = requests.get(api_url)
    logger.info({"response.status_code": response.status_code})

    if response.status_code == 200:
        return JsonResponse(
            {"message": f"Frontend reached API at {api_url}"}, status=200
        )
    else:
        return JsonResponse(
            {"message": f"Frontend failed to reach API at {api_url}"},
            status=response.status_code,
        )


def ipfilter(request):
    return JsonResponse({"message": f"Success"}, status=200)


@login_required
def sso(request):
    if not request.user.is_authenticated and request.session.get(
        TOKEN_SESSION_KEY, None
    ):
        return redirect(settings.LOGIN_URL)
    return redirect("index")


def ipfilter_basic_auth(request):
    auth_header = request.META.get("HTTP_AUTHORIZATION")
    if auth_header:
        auth_type, auth_string = auth_header.split(" ", 1)
        if auth_type.lower() == "basic":
            decoded_creds = base64.b64decode(auth_string).decode("utf-8")
            username, password = decoded_creds.split(":", 1)

            if (
                username == settings.BASIC_AUTH_USERNAME
                and password == settings.BASIC_AUTH_PASSWORD
            ):
                ipfilter_url = reverse("ipfilter")
                response = HttpResponseRedirect(ipfilter_url)
                response.headers["Authorization"] = f"Basic {auth_string}"

                return response

    response = HttpResponse("Unauthorized", status=401)
    response["WWW-Authenticate"] = 'Basic realm="Login Required"'

    return response
