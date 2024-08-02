import os
from datetime import datetime
from http import HTTPStatus

from playwright.sync_api import Page

def test_api_response(page: Page):
    page.clock.pause_at(datetime.datetime(1234, 5, 6))
    landing_page_url = os.getenv("LANDING_PAGE_URL")
    response = page.goto(f"{landing_page_url}/api/")
    
    assert response.status == HTTPStatus.OK
    
    response_data = response.json()
    
    assert response_data['message'] == "Success"
    
    timestamp_str = response_data['timestamp']
    timestamp = datetime.fromisoformat(timestamp_str)
    expected_timestamp = datetime(1234, 5, 6)

    assert timestamp == expected_timestamp
    