from unittest.mock import patch, Mock

from app import views


@patch('app.check.check_http.requests')
def test_http_view(patched_requests, mock_environment):
    mock_environment('HTTP_CHECK_URLS', 'https://example.com')
    patched_requests.get.return_value = Mock(status_code=200)

    response = views.http_check()
    assert 'HTTP Checks' in response
    assert '✓' in response
    assert 'https://example.com' in response
