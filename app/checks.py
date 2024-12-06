import json
import os
from datetime import datetime

import boto3
import redis
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.db import connections
from opensearchpy import OpenSearch
from tenacity import RetryError
from tenacity import retry
from tenacity import stop_after_delay
from tenacity import wait_fixed

from celery_worker.tasks import demodjango_task

from .check.check_http import HTTPCheck
from .util import Check
from .util import CheckResult


def read_from_bucket(bucket_name):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    body = bucket.Object("sample_file.txt")
    return f'{body.get()["Body"].read().decode()}Bucket: {bucket_name}'


class PostgresRdsCheck(Check):
    def __init__(self):
        super().__init__("postgres_rds", "PostgreSQL (RDS)")

    def __call__(self):
        try:
            if not os.environ.get("RDS_POSTGRES_CREDENTIALS"):
                raise Exception("No RDS database")

            with connections["default"].cursor() as c:
                c.execute("SELECT version()")
                return [self.result(True, c.fetchone()[0])]
        except Exception as e:
            return [self.result(False, str(e))]


class CeleryWorkerCheck(Check):
    def __init__(self, logger):
        super().__init__("celery", "Celery Worker", logger=logger)

    def __call__(self):
        from demodjango import celery_app

        get_result_timeout = 2

        @retry(stop=stop_after_delay(get_result_timeout), wait=wait_fixed(1))
        def get_result_from_celery_backend():
            self.logger.info("Getting result from Celery backend")
            backend_result = json.loads(
                celery_app.backend.get(f"celery-task-meta-{task_id}")
            )
            self.logger.debug("backend_result")
            self.logger.debug(backend_result)
            if backend_result["status"] != "SUCCESS":
                raise Exception
            return backend_result

        try:
            timestamp = datetime.utcnow()
            self.logger.info("Adding debug task to Celery queue")
            task_id = str(demodjango_task.delay(f"{timestamp}"))
            backend_result = get_result_from_celery_backend()
            connection_info = f"{backend_result['result']} with task_id {task_id} was processed at {backend_result['date_done']} with status {backend_result['status']}"
            return [self.result(True, connection_info)]
        except RetryError:
            connection_info = f"task_id {task_id} was not processed within {get_result_timeout} seconds"
            self.logger.error(connection_info)
            return [self.result(False, connection_info)]
        except Exception as e:
            self.logger.error(e)
            return [self.result(False, str(e))]


class CeleryBeatCheck(Check):
    def __init__(self):
        super().__init__("beat", "Celery Beat")

    def __call__(self):
        from .models import ScheduledTask

        try:
            if not os.environ.get("RDS_POSTGRES_CREDENTIALS"):
                raise Exception("Database not found")

            latest_task = ScheduledTask.objects.all().order_by("-timestamp").first()
            connection_info = f"Latest task scheduled with task_id {latest_task.taskid} at {latest_task.timestamp}"
            return [self.result(True, connection_info)]
        except Exception as e:
            return [self.result(False, str(e))]


class RedisCheck(Check):
    def __init__(self):
        super().__init__("redis", "Redis")

    def __call__(self):
        try:
            r = redis.Redis.from_url(f"{settings.REDIS_ENDPOINT}")
            return [self.result(True, r.get("test-data").decode())]
        except Exception as e:
            return [self.result(False, str(e))]


class ServerTimeCheck(Check):
    def __init__(self):
        super().__init__("server_time", "Server Time")

    def __call__(self):
        return [self.result(True, str(datetime.utcnow()))]


class GitInformationCheck(Check):
    def __init__(self):
        super().__init__("git_information", "Git information")

    def __call__(self):
        git_commit = os.environ.get("GIT_COMMIT", "Unknown")
        git_branch = os.environ.get("GIT_BRANCH", "Unknown")
        git_tag = os.environ.get("GIT_TAG", "Unknown")

        return [
            self.result(
                git_commit != "Unknown",
                f"Commit: {git_commit}, Branch: {git_branch}, Tag: {git_tag}",
            )
        ]


class HttpConnectionCheck(Check):
    def __init__(self):
        super().__init__("http", "HTTP Checks")

    def __call__(self):
        urls = os.environ.get("HTTP_CHECK_URLS", "https://httpstat.us/200|200|GET")

        check = HTTPCheck(urls)
        check.execute()

        return [
            self.result(
                check.success,
                "".join([c.render() for c in check.report]),
            )
        ]


class PrivateSubmoduleCheck(Check):
    def __init__(self):
        super().__init__("private_submodule", "Private submodule")

    def __call__(self):
        file_path = "platform-demo-private/sample.txt"
        success = False
        connection_info = (
            f"Failed to read file from private submodule at path: {file_path}"
        )

        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                content = file.read()
                if "lorem ipsum" in content.lower():
                    success = True
                    connection_info = f"Successfully built sample.txt file in private submodule at: {file_path}"

        return [self.result(success, connection_info)]


class ReadWriteCheck(Check):
    def __init__(self):
        super().__init__("read_write", "Filesystem read/write")

    def __call__(self):
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
            return [self.result(True, read_write_status)]
        except Exception as e:
            return [self.result(False, str(e))]


class S3AdditionalBucketCheck(Check):
    def __init__(self):
        super().__init__("s3_additional", "S3 Additional Bucket")

    def __call__(self):
        try:
            result = read_from_bucket(settings.ADDITIONAL_S3_BUCKET_NAME)
            return [self.result(True, result)]
        except Exception as e:
            return [self.result(False, str(e))]


class S3StaticBucketCheck(Check):
    def __init__(self):
        super().__init__("s3_static", "S3 Bucket for static assets")

    def __call__(self):
        try:
            response = requests.get(f"{settings.STATIC_S3_ENDPOINT}/test.html")
            if response.status_code == 200:
                parsed_html = BeautifulSoup(response.text, "html.parser")
                test_text = parsed_html.body.find("p").text
                return [self.result(True, test_text)]

            raise Exception(
                f"Failed to get static asset with status code: {response.status_code}"
            )
        except Exception as e:
            return [self.result(False, str(e))]


class S3BucketCheck(Check):
    def __init__(self):
        super().__init__("s3", "S3 Bucket")

    def __call__(self):
        try:
            result = read_from_bucket(settings.S3_BUCKET_NAME)
            return [self.result(True, result)]
        except Exception as e:
            return [self.result(False, str(e))]


class S3CrossEnvironmentBucketChecks(Check):
    def __init__(self):
        super().__init__("s3_cross_environment", "Cross environment S3 Buckets")

    def __call__(self):
        buckets = [
            bucket.strip()
            for bucket in settings.S3_CROSS_ENVIRONMENT_BUCKET_NAMES.split(",")
            if bucket.strip()
        ]
        check_results = []
        if not buckets:
            return [
                CheckResult(
                    "debug_s3_cross_environment",
                    f"{self.description}",
                    True,
                    "No cross-environment buckets configured",
                )
            ]
        for bucket in buckets:
            try:
                result = read_from_bucket(bucket)
                check_results.append(
                    CheckResult(
                        self.test_id, f"{self.description} ({bucket})", True, result
                    )
                )
            except Exception as e:
                check_results.append(
                    CheckResult(
                        self.test_id,
                        f"{self.description} ({bucket})",
                        False,
                        f"Error reading {bucket}: {str(e)}",
                    )
                )
        return check_results


class OpensearchCheck(Check):
    def __init__(self, logger):
        super().__init__("opensearch", "OpenSearch", logger=logger)

    def __call__(self):
        get_result_timeout = 5

        @retry(stop=stop_after_delay(get_result_timeout), wait=wait_fixed(1))
        def read_content_from_opensearch():
            opensearch_client = OpenSearch(f"{settings.OPENSEARCH_ENDPOINT}")
            results = opensearch_client.get(index="test-index", id=1)
            return results

        try:
            results = read_content_from_opensearch()
            return [self.result(True, results["_source"]["text"])]
        except RetryError:
            connection_info = f"Unable to read content from {self.description} within {get_result_timeout} seconds"
            self.logger.error(connection_info)
            return [self.result(False, connection_info)]
        except Exception as e:
            return [self.result(False, str(e))]
