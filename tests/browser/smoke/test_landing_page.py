import os
import re
from http import HTTPStatus

from normality import slugify
from playwright.sync_api import Page, expect

from app.util import STATUS_SUCCESS
from app.views import (
    ALL_CHECKS,
    CELERY,
    BEAT,
    GIT_INFORMATION,
    OPENSEARCH,
    POSTGRES_RDS,
    READ_WRITE,
    REDIS,
    S3,
    SERVER_TIME,
    HTTP_CONNECTION,
)


def test_page_loads_with_title_and_has_success_ticks(page: Page):
    response = page.goto(os.getenv("LANDING_PAGE_URL"))

    assert response.status == HTTPStatus.OK

    expect(page).to_have_title(re.compile("DemoDjango"))

    expect(
        page.get_by_test_id(slugify(ALL_CHECKS[SERVER_TIME]))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify(ALL_CHECKS[GIT_INFORMATION]))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify(ALL_CHECKS[POSTGRES_RDS]))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify(ALL_CHECKS[READ_WRITE]))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify(ALL_CHECKS[REDIS]))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify(ALL_CHECKS[S3]))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify(ALL_CHECKS[OPENSEARCH]))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify(ALL_CHECKS[CELERY]))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify(ALL_CHECKS[BEAT]))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify(ALL_CHECKS[HTTP_CONNECTION]))
    ).to_have_text(re.compile(STATUS_SUCCESS))
