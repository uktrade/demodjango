import base64
import json
from unittest.mock import Mock
from unittest.mock import patch

import requests
from django.test import override_settings
from django.urls import reverse
from freezegun import freeze_time

from app import views


@patch("app.check.check_http.requests")
def test_http_view(patched_requests, mock_environment):
    mock_environment("HTTP_CHECK_URLS", "https://example.com")
    patched_requests.get.return_value = Mock(status_code=200)

    response = views.http_check()
    assert "HTTP Checks" in response
    assert "✓" in response
    assert "https://example.com" in response


@override_settings(ROOT_URLCONF="tests.api_urls")
@freeze_time("2024-08-01 12:34:56")
def test_api_view(client):
    response = client.get("/")
    response_data = json.loads(response.content)

    assert response.status_code == 200
    assert response_data["message"] == "Success"
    assert response_data["timestamp"] == "2024-08-01T12:34:56"


@override_settings(ROOT_URLCONF="tests.api_urls")
@patch("app.views.reverse")
@patch("app.views.requests.get")
def test_test_web(mock_get, mock_reverse, client):
    mock_reverse.return_value = "https://internal.api.local.demodjango.uktrade.digital/"
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    response = client.get("/test-web/")
    response_data = json.loads(response.content)

    mock_get.assert_called_once_with(
        "https://internal.local.demodjango.uktrade.digital/"
    )
    assert (
        response_data["message"]
        == "API reached web service at https://internal.local.demodjango.uktrade.digital/"
    )
    assert response.status_code == 200


@override_settings(
    BASIC_AUTH_USERNAME="valid_user", BASIC_AUTH_PASSWORD="valid_password"
)
def test_ipfilter_basic_auth_success(client):
    credentials = "valid_user:valid_password"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    response = client.get(
        "/ipfilter-basic-auth/", HTTP_AUTHORIZATION=f"Basic {encoded_credentials}"
    )

    assert response.status_code == 302
    assert response.url == reverse("ipfilter")
    assert response["Authorization"] == f"Basic {encoded_credentials}"


@override_settings(
    BASIC_AUTH_USERNAME="valid_user", BASIC_AUTH_PASSWORD="valid_password"
)
def test_ipfilter_basic_auth_invalid_credentials(client):
    invalid_credentials = "invalid_user:invalid_password"
    encoded_invalid_credentials = base64.b64encode(
        invalid_credentials.encode("utf-8")
    ).decode("utf-8")

    response = client.get(
        "/ipfilter-basic-auth/",
        HTTP_AUTHORIZATION=f"Basic {encoded_invalid_credentials}",
    )

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == 'Basic realm="Login Required"'


def test_ipfilter_basic_auth_no_auth_header(client):
    response = client.get("/ipfilter-basic-auth/")

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == 'Basic realm="Login Required"'


@override_settings(
    BASIC_AUTH_USERNAME="valid_user", BASIC_AUTH_PASSWORD="valid_password"
)
def test_ipfilter_basic_auth_invalid_auth_type(client):
    credentials = "valid_user:valid_password"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    response = client.get(
        "/ipfilter-basic-auth/", HTTP_AUTHORIZATION=f"Bearer {encoded_credentials}"
    )

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == 'Basic realm="Login Required"'


def test_ipfilter_basic_auth_malformed_auth_header(client):
    malformed_header = "BasicMalformedHeader"

    response = client.get(
        "/ipfilter-basic-auth/", {"HTTP_AUTHORIZATION": malformed_header}
    )

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == 'Basic realm="Login Required"'


def test_sso_success(client):
    response = client.get(reverse('sso'))
    response_data = json.loads(response.content.decode())
    assert response.status_code == 200
    assert response_data["message"] == "Success"