import json
from unittest.mock import patch, Mock

from django.test import Client
from django.urls import reverse
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


@freeze_time("2024-08-01 12:34:56")
def test_api_view(client):
    response = client.get(reverse('api'))
    response_data = json.loads(response.content)
    
    assert response.status_code == 200
    assert response_data['message'] == "Success"
    assert response_data['timestamp'] == "2024-08-01T12:34:56"
