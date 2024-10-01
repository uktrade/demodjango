import re

from normality import slugify
from playwright.sync_api import Page
from playwright.sync_api import expect

from app.util import STATUS_SUCCESS
from app.views import ALL_CHECKS
from app.views import BEAT
from app.views import CELERY
from app.views import GIT_INFORMATION
from app.views import HTTP_CONNECTION
from app.views import OPENSEARCH
from app.views import POSTGRES_RDS
from app.views import READ_WRITE
from app.views import REDIS
from app.views import S3
from app.views import S3_ADDITIONAL
from app.views import SERVER_TIME


def assert_landing_page_has_normal_content(page: Page):
    expect(page).to_have_title(re.compile("DemoDjango"))

    expect(page.get_by_test_id(slugify(ALL_CHECKS[SERVER_TIME]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )

    expect(page.get_by_test_id(slugify(ALL_CHECKS[GIT_INFORMATION]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )

    expect(page.get_by_test_id(slugify(ALL_CHECKS[POSTGRES_RDS]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )

    expect(page.get_by_test_id(slugify(ALL_CHECKS[READ_WRITE]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )

    expect(page.get_by_test_id(slugify(ALL_CHECKS[REDIS]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )

    expect(page.get_by_test_id(slugify(ALL_CHECKS[S3]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )
    
    expect(page.get_by_test_id(slugify(ALL_CHECKS[S3_ADDITIONAL]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )

    expect(page.get_by_test_id(slugify(ALL_CHECKS[OPENSEARCH]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )

    expect(page.get_by_test_id(slugify(ALL_CHECKS[CELERY]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )

    expect(page.get_by_test_id(slugify(ALL_CHECKS[BEAT]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )

    expect(page.get_by_test_id(slugify(ALL_CHECKS[HTTP_CONNECTION]))).to_have_text(
        re.compile(STATUS_SUCCESS)
    )


# CDN domain has just the basic bootstrap page.
def assert_landing_page_has_normal_content_cdn(page: Page):
    expect(page).to_have_title(re.compile("Service Bootstrap"))
