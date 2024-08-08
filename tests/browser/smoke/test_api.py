import json
import os
from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from playwright.sync_api import Page

def is_approx_now(time: datetime):
    now = datetime.now()
    tolerance = timedelta(seconds=60)
    
    return abs(now - time) <= tolerance

def test_api_response(page: Page):
    landing_page_url = os.getenv("LANDING_PAGE_URL")
    api_url = landing_page_url.replace("https://internal.", "https://internal.api.")
    
    response = page.goto(api_url)
    
    assert response.status == 200
    
    response_data = response.json()
    
    assert response_data['message'] == "Success"
    
    timestamp_str = response_data['timestamp']
    time = datetime.fromisoformat(timestamp_str)
    
    assert is_approx_now(time)
