import os

from playwright.sync_api import Page
from playwright.sync_api import expect

from tests.browser.src.landing_page_checks import assert_landing_page_has_normal_content, assert_landing_page_has_normal_content_cdn


def test_page_loads_ok_and_shows_default_offline_message(page: Page):
    response = page.goto(os.getenv("LANDING_PAGE_URL"))

    assert response.status == 503

    expect(page.locator("body")).to_contain_text(
        "The service is currently unavailable. Don't worry, we'll be back soon."
    )


def test_with_bypass_header_page_loads_ok_with_normal_content(page: Page):
    MAINTENANCE_PAGE_BYPASS_VALUE = os.getenv("MAINTENANCE_PAGE_BYPASS_VALUE")
    page.context.route(
        "**/*",
        lambda route, request: route.continue_(
            headers={**request.headers, "Bypass-Key": MAINTENANCE_PAGE_BYPASS_VALUE}
        ),
    )

    response = page.goto(os.getenv("LANDING_PAGE_URL"))

    assert response.status == 200

    if os.getenv("IS_CDN"):
        assert_landing_page_has_normal_content_cdn(page)
    else:
        assert_landing_page_has_normal_content(page)
