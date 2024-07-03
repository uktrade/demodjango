import os
from http import HTTPStatus

from playwright.sync_api import Page, expect

from tests.browser.src.landing_page_checks import assert_landing_page_has_normal_content


def test_page_loads_ok_and_shows_default_offline_message(page: Page):
    response = page.goto(os.getenv("LANDING_PAGE_URL"))

    assert response.status == HTTPStatus.OK

    expect(page.locator('body')).to_have_text("put default message here")


def test_with_bypass_header_page_loads_ok_with_normal_content(page: Page):
    response = page.goto(os.getenv("LANDING_PAGE_URL"))

    assert response.status == HTTPStatus.OK

    assert_landing_page_has_normal_content(page)

# Todo: check env ip is whitelisted, is this a browser test or actually a curl etc. job?
