import time
import os
from playwright.sync_api import Page

def test_sso_flow(page: Page):
    landing_page_url = os.getenv("LANDING_PAGE_URL")
    IS_CDN = os.getenv("IS_CDN")
    if IS_CDN:
        landing_page_url = landing_page_url.replace("https://", "https://internal.")
    full_url = f"{landing_page_url}sso"
    
    response = page.goto(full_url)
    time.sleep(2)
    
    current_url = page.url
    assert "sso" in current_url
    assert response.status == 200
