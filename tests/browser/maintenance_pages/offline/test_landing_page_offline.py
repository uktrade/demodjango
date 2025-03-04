# These tests are not meant to be run in isolation, they all run as part of platform-tools/regression_tests/stages/run_maintenance_page_tests.sh

import os

from playwright.sync_api import Page
from playwright.sync_api import expect

from tests.browser.src.landing_page_checks import assert_landing_page_has_normal_content

def test_maintenance_page_loads_ok_and_shows_default_offline_message(page: Page):
    response = page.goto(os.getenv("IP_FILTER_TEST_URL"))

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

    response = page.goto(os.getenv("IP_FILTER_TEST_URL"))

    assert response.status == 200
    assert_landing_page_has_normal_content(page)


def test_frontend_to_api(page: Page):
    MAINTENANCE_PAGE_BYPASS_VALUE = os.getenv("MAINTENANCE_PAGE_BYPASS_VALUE")
    page.context.route(
        "**/*",
        lambda route, request: route.continue_(
            headers={**request.headers, "Bypass-Key": MAINTENANCE_PAGE_BYPASS_VALUE}
        ),
    )
    
    ip_filter_test_service_url = os.getenv("IP_FILTER_TEST_URL")
    test_api_url = f"{ip_filter_test_service_url}test-api/"
    
    expected_api_service_url = os.getenv("API_SERVICE_URL")

    response = page.goto(test_api_url)
    response_data = response.json()

    assert response.status == 200
    assert (
        response_data["message"]
        == f"Frontend reached API at {expected_api_service_url}"
    )
