import os

from playwright.sync_api import Page


def setup_basic_auth(page):
    username = os.getenv("BASIC_AUTH_USERNAME")
    password = os.getenv("BASIC_AUTH_PASSWORD")
    context = page.context.browser.new_context(
        http_credentials={"username": username, "password": password}
    )

    return context.new_page()


def test_ipfilter_endpoint(page: Page):
    landing_page_url = os.getenv("LANDING_PAGE_URL")
    IS_CDN = os.getenv("IS_CDN")
    if IS_CDN:
        landing_page_url = landing_page_url.replace("https://", "https://internal.")
    page = setup_basic_auth(page)
    response = page.goto(f"{landing_page_url}/ipfilter")

    assert response.status == 200
    assert response.text() == "ok"


def test_ipfilter_basic_auth_endpoint(page: Page):
    landing_page_url = os.getenv("LANDING_PAGE_URL")
    IS_CDN = os.getenv("IS_CDN")
    if IS_CDN:
        landing_page_url = landing_page_url.replace("https://", "https://internal.")
    response = page.goto(f"{landing_page_url}ipfilter-basic-auth")
    assert response.status == 401
    assert response.headers["www-authenticate"] == 'Basic realm="Login Required"'

    page = setup_basic_auth(page)

    response = page.goto(f"{landing_page_url}ipfilter-basic-auth")

    assert response.status == 200
    assert response.text() == "ok"
