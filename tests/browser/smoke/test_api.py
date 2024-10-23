import os
from datetime import datetime
from datetime import timedelta

from playwright.sync_api import Page


def is_approx_now(time: datetime):
    now = datetime.now()
    tolerance = timedelta(seconds=60)

    return abs(now - time) <= tolerance


def test_api_response(page: Page):
    api_service_url = os.getenv("API_SERVICE_URL")

    response = page.goto(api_service_url)

    assert response.status == 200

    response_data = response.json()

    assert response_data["message"] == "Success"

    timestamp_str = response_data["timestamp"]
    time = datetime.fromisoformat(timestamp_str)

    assert is_approx_now(time)


if os.getenv("IS_API"):

    def test_web_response(page: Page):
        web_service_url = os.getenv("WEB_SERVICE_URL")
        api_url = web_service_url.replace("https://internal.", "https://internal.api.")

        response = page.goto(f"{api_url}test-web")

        assert response.status == 200

        response_data = response.json()

        assert response_data["message"] == "API reached web service"
