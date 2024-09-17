import os
from http import HTTPStatus

from playwright.sync_api import Page

from tests.browser.src.landing_page_checks import assert_landing_page_has_normal_content, assert_landing_page_has_normal_content_cdn


def test_page_loads_with_title_and_has_success_ticks(page: Page):
    response = page.goto(os.getenv("LANDING_PAGE_URL"))

    assert response.status == HTTPStatus.OK
    if os.getenv("IS_CDN"):
        assert_landing_page_has_normal_content_cdn(page)
    else:
        assert_landing_page_has_normal_content(page)
