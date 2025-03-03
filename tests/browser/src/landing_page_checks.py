import re

from normality import slugify
from playwright.sync_api import Page
from playwright.sync_api import expect

from app.util import STATUS_SUCCESS
from app.views import MANDATORY_CHECKS


def assert_landing_page_has_normal_content(page: Page):
    expect(page).to_have_title(re.compile("DemoDjango"))

    for check in MANDATORY_CHECKS:
        expect(
            page.get_by_test_id(slugify(check.description)),
            f"Green tick expected for test: {check.test_id}",
        ).to_have_text(STATUS_SUCCESS)
