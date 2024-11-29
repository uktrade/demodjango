import base64
import json
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests
from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from freezegun import freeze_time

from app.views import MANDATORY_CHECKS, HttpConnectionCheck

TOKEN_SESSION_KEY = "auth_token"


@patch("app.check.check_http.requests")
def test_http_view(patched_requests, mock_environment):
    mock_environment("HTTP_CHECK_URLS", "https://example.com")
    patched_requests.get.return_value = Mock(status_code=200)
    check = HttpConnectionCheck()
    response = check()[0]
    assert "HTTP Checks" == response.description
    assert "http" == response.test_id
    assert response.success
    assert "https://example.com" in response.message


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


@patch("app.views.reverse")
@patch("app.views.requests.get")
def test_test_api(mock_get, mock_reverse, client):
    mock_reverse.return_value = "https://web.local.demodjango.uktrade.digital/"
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    response = client.get("/test-api/")
    response_data = json.loads(response.content)

    assert (
        response_data["message"]
        == "Frontend reached API at https://api.local.demodjango.uktrade.digital/"
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


def test_login_required_when_accessing_sso(client):
    response = client.get("/sso/")
    assert response.status_code == 302


@pytest.mark.django_db
def test_sso_successfully_redirects_when_authenticated(client):
    User.objects.create_user(
        username="john", email="lennon@thebeatles.com", password="johnpassword"
    )

    client.login(username="john", password="johnpassword")

    session = client.session
    session[TOKEN_SESSION_KEY] = TOKEN_SESSION_KEY
    session.save()

    response = client.get("/sso/")

    assert response.status_code == 302
    assert response.url == reverse("index")


@pytest.mark.django_db
def test_sso_redirects_when_not_authenticated(client):
    session = client.session
    session[TOKEN_SESSION_KEY] = None
    session.save()

    response = client.get(reverse("sso"))

    assert response.status_code == 302
    assert response.url == "/auth/login/?next=/sso/"


FAST_CHECK_SUBSET = ["s3", "s3_cross_environment"]


@pytest.mark.django_db
@override_settings(S3_CROSS_ENVIRONMENT_BUCKET_NAMES="xe_bucket_1,xe_bucket_2")
@override_settings(ACTIVE_CHECKS="s3, s3_cross_environment")
def test_index_with_json_query_string_returns_json(client):
    session = client.session
    session[TOKEN_SESSION_KEY] = None
    session.save()

    response = client.get("/?json=true")
    check_results = json.loads(response.content)["check_results"]

    print(f"RESULT:{json.dumps(check_results, indent=2)}")

    assert (
        len(
            [
                res
                for res in check_results
                if res["description"] == "Cross environment S3 Buckets (xe_bucket_1)"
            ]
        )
        == 1
    )
    assert (
        len(
            [
                res
                for res in check_results
                if res["description"] == "Cross environment S3 Buckets (xe_bucket_2)"
            ]
        )
        == 1
    )
    assert (
        len([res for res in check_results if res["description"] == "Git information"])
        == 1
    )
    assert (
        len([res for res in check_results if res["description"] == "Server Time"]) == 1
    )
    assert response.status_code == 200
