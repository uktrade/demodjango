import re
from playwright.sync_api import Page, expect

from normality import slugify
from app.util import STATUS_SUCCESS

LOCAL_ENVIRONMENT_URL = "http://localhost:8080/"
DEV_ENVIRONMENT_URL = "https://v2.demodjango.dev.uktrade.digital/"
PAGE_TITLE = "DemoDjango"


def test_has_title(page: Page):
    page.goto(LOCAL_ENVIRONMENT_URL)

    expect(page).to_have_title(re.compile(PAGE_TITLE))


def test_has_success_tick_symbols(page: Page):
    page.goto(LOCAL_ENVIRONMENT_URL)

    expect(
        page.get_by_test_id(slugify('PostgreSQL (Aurora)'))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify('SQLite3'))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify('Redis'))
    ).to_have_text(re.compile(STATUS_SUCCESS))
    expect(
        page.get_by_test_id(slugify('S3 Bucket'))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify('OpenSearch'))
    ).to_have_text(re.compile(STATUS_SUCCESS))

    expect(
        page.get_by_test_id(slugify('Celery Worker'))
    ).to_have_text(re.compile(STATUS_SUCCESS))
