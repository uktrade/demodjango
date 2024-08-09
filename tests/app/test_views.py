import json
from unittest.mock import patch, Mock

import requests
from django.test import override_settings
from freezegun import freeze_time

from app import views


@patch('app.check.check_http.requests')
def test_http_view(patched_requests, mock_environment):
    mock_environment('HTTP_CHECK_URLS', 'https://example.com')
    patched_requests.get.return_value = Mock(status_code=200)

    response = views.http_check()
    assert 'HTTP Checks' in response
    assert '✓' in response
    assert 'https://example.com' in response

@override_settings(IS_API=True)
@freeze_time("2024-08-01 12:34:56")
def test_api_view(client):
    response = client.get("/")
    response_data = json.loads(response.content)
    
    assert response.status_code == 200
    assert response_data["message"] == "Success"
    assert response_data["timestamp"] == "2024-08-01T12:34:56"

@override_settings(IS_API=True)
@patch("app.views.reverse")
@patch("app.views.requests.get")
def test_test_web(mock_get, mock_reverse, client):
    mock_reverse.return_value = "https://internal.api.local.demodjango.uktrade.digital/"
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    response = client.get("/test-web/")
    response_data = json.loads(response.content)
    
    mock_get.assert_called_once_with("https://internal.local.demodjango.uktrade.digital/")
    assert response_data["message"] == "API reached web service"
    assert response.status_code == 200
    