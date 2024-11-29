import base64
import logging
import os
from datetime import datetime

from app.checks import (
    CeleryBeatCheck,
    CeleryWorkerCheck,
    GitInformationCheck,
    HttpConnectionCheck,
    OpensearchCheck,
    PostgresRdsCheck,
    PrivateSubmoduleCheck,
    ReadWriteCheck,
    RedisCheck,
    S3AdditionalBucketCheck,
    S3BucketCheck,
    S3CrossEnvironmentBucketChecks,
    S3StaticBucketCheck,
    ServerTimeCheck,
)
import requests
from authbroker_client.utils import TOKEN_SESSION_KEY
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from .util import render_connection_info

logger = logging.getLogger("django")

MANDATORY_CHECKS = [
    GitInformationCheck("git_information", "Git information"),
    ServerTimeCheck("server_time", "Server Time"),
]

OPTIONAL_CHECKS = [
    CeleryBeatCheck("beat", "Celery Worker"),
    CeleryWorkerCheck("celery", "Celery Worker", logger),
    HttpConnectionCheck("http", "HTTP Checks"),
    OpensearchCheck("opensearch", "OpenSearch", logger),
    PostgresRdsCheck("postgres_rds", "PostgreSQL (RDS)"),
    PrivateSubmoduleCheck("private_submodule", "Private submodule"),
    ReadWriteCheck("read_write", "Filesystem read/write"),
    RedisCheck("redis", "Redis"),
    S3BucketCheck("s3", "S3 Bucket"),
    S3AdditionalBucketCheck("s3_additional", "S3 Additional Bucket"),
    S3StaticBucketCheck("s3_static", "S3 Bucket for static assets"),
    S3CrossEnvironmentBucketChecks(
        "s3_cross_environment", "Cross environment S3 Buckets"
    ),
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

    active_checks = MANDATORY_CHECKS + [
        check
        for check in OPTIONAL_CHECKS
        if not settings.ACTIVE_CHECKS or check.test_id in settings.ACTIVE_CHECKS
    ]

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
