import base64
import json
import logging
import os
from datetime import datetime

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


class PostgresRdsCheck(Check):
    def __call__(self):
        try:
            if not os.environ.get("RDS_POSTGRES_CREDENTIALS"):
                raise Exception("No RDS database")

            with connections["default"].cursor() as c:
                c.execute("SELECT version()")
                return [CheckResult(self.test_id, self.description, True, c.fetchone()[0])]
        except Exception as e:
            return [CheckResult(self.test_id, self.description, False, str(e))]
        

class CeleryWorkerCheck(Check):
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
            return [CheckResult(self.test_id, self.description, True, connection_info)]
        except RetryError:
            connection_info = (
                f"task_id {task_id} was not processed within {get_result_timeout} seconds"
            )
            self.logger.error(connection_info)
            return [CheckResult(self.test_id, self.description, False, connection_info)]
        except Exception as e:
            self.logger.error(e)
            return [CheckResult(self.test_id, self.description, False, str(e))]