import os
import time

from playwright.sync_api import Page


def test_sso_flow(page: Page):
    landing_page_url = os.getenv("LANDING_PAGE_URL")
    full_url = f"{landing_page_url}sso"

    response = page.goto(full_url)
    time.sleep(2)

    current_url = page.url
    assert "sso" in current_url
    assert response.status == 200
