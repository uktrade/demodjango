import os

from playwright.sync_api import Page
from playwright.sync_api import expect

from tests.browser.src.landing_page_checks import assert_landing_page_has_normal_content
from tests.browser.src.landing_page_checks import (
    assert_landing_page_has_normal_content_cdn,
)


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


def test_frontend_to_api(page: Page):
    if os.getenv("IS_CDN"):
        return

    MAINTENANCE_PAGE_BYPASS_VALUE = os.getenv("MAINTENANCE_PAGE_BYPASS_VALUE")
    page.context.route(
        "**/*",
        lambda route, request: route.continue_(
            headers={**request.headers, "Bypass-Key": MAINTENANCE_PAGE_BYPASS_VALUE}
        ),
    )
    landing_page_url = os.getenv("LANDING_PAGE_URL")
    test_api_url = f"{landing_page_url}test-api"
    parts = landing_page_url.split(".", 1)
    expected_url = f"{parts[0]}.api.{parts[1]}"

    response = page.goto(test_api_url)
    response_data = response.json()

    assert response.status == 200
    assert response_data["message"] == f"Frontend reached API at {expected_url}"
