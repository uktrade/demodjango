import time
import os
from playwright.sync_api import Page


def test_sso_flow(page: Page):
    web_service_url = os.getenv("WEB_SERVICE_URL")
    full_url = f"{web_service_url}sso"

    response = page.goto(full_url)
    time.sleep(2)

    current_url = page.url
    assert "sso" in current_url
    assert response.status == 200
