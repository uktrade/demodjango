import json
import os
from datetime import datetime
from datetime import timezone
from unittest.mock import patch

from playwright.sync_api import Page

def mock_server_time(route):
    mock_data = {
        "message": "Success",
        "timestamp": datetime(2101, 2, 3, tzinfo=timezone.utc).isoformat()
    }
    
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(mock_data)
    )


def test_api_response(page: Page):
    page.route("**/api/", mock_server_time)

    landing_page_url = os.getenv("LANDING_PAGE_URL")
    response = page.goto(f"{landing_page_url}/api/")
    
    assert response.status == 200
    
    response_data = response.json()
    
    assert response_data['message'] == "Success"
    
    timestamp_str = response_data['timestamp']
    timestamp = datetime.fromisoformat(timestamp_str)
    expected_timestamp = datetime(2101, 2, 3, tzinfo=timezone.utc)

    assert timestamp == expected_timestamp