from unittest.mock import MagicMock, patch, Mock, call

import pytest
from requests.exceptions import RequestException

from app.check.check_http import HTTPCheck

URL_ONLY = 'https://example.com'
URL_AND_STATUS = 'https://example.com|200'
URL_STATUS_AND_METHOD = 'https://example.com|200|GET'


@pytest.mark.parametrize('definition', [URL_ONLY, URL_AND_STATUS, URL_STATUS_AND_METHOD])
@patch('app.check.check_http.requests')
def test_a_successful_single_http_check(patched_requests, definition):
    patched_requests.get.return_value = Mock(status_code=200)

    check = HTTPCheck(definition)
    check.execute()

    assert check.success
    assert definition == check.report[0].summary
    assert not check.report[0].errors
    assert check.report[0].success
    patched_requests.get.assert_called_with('https://example.com')


@patch('app.check.check_http.requests')
def test_a_successful_set_of_http_checks(patched_requests):
    patched_requests.get.return_value = Mock(status_code=200)

    check = HTTPCheck(','.join([URL_ONLY, URL_AND_STATUS, URL_STATUS_AND_METHOD]))
    check.execute()

    assert check.success
    assert 3 == len(check.report)
    assert 'https://example.com' == check.report[0].summary
    assert 'https://example.com|200' == check.report[1].summary
    assert 'https://example.com|200|GET' == check.report[2].summary


@patch('app.check.check_http.requests')
def test_a_failed_http_check_status_code_mismatch(patched_requests):
    patched_requests.get.return_value = Mock(status_code=400)

    check = HTTPCheck(URL_STATUS_AND_METHOD)
    check.execute()

    assert not check.success
    assert 'https://example.com|200|GET' in check.report[0].summary
    assert 'expected HTTP Status 200 but got 400' in check.report[0].errors
    patched_requests.get.assert_called_with('https://example.com')


@pytest.mark.parametrize('definition,message,error', [
    ('not-a-valid-url', 'not-a-valid-url', '"not-a-valid-url" is not a valid URL'),
    ('https://example.com|POST', 'https://example.com|POST',
     'expected status code to be integer, got POST'),
    ('https://example.com|200|WHAT', 'https://example.com|200|WHAT',
     'method "WHAT" is not a valid HTTP method'),
    ('9999', '9999', '"9999" is not a valid URL'),
])
def test_a_failed_http_check_due_to_invalid_configuration(definition, message, error):
    check = HTTPCheck(definition)
    check.execute()

    assert not check.success
    assert 1 == len(check.report)
    assert not check.report[0].success
    assert message == check.report[0].summary
    assert error in check.report[0].errors


@patch('app.check.check_http.requests')
def test_a_failed_http_check_due_to_exception(patched_requests):
    patched_requests.get.side_effect = RequestException("Fake Exception")

    check = HTTPCheck('https://example.com')
    check.execute()

    assert not check.success
    assert 1 == len(check.report)
    assert not check.report[0].success
    assert 'Fake Exception' in check.report[0].errors
    assert 'https://example.com' == check.report[0].summary
