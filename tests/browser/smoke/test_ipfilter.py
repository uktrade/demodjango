# import os

# from playwright.sync_api import Page


# def setup_basic_auth(page):
#     username = os.getenv("BASIC_AUTH_USERNAME")
#     password = os.getenv("BASIC_AUTH_PASSWORD")
#     context = page.context.browser.new_context(
#         http_credentials={"username": username, "password": password}
#     )

#     return context.new_page()


# def test_ipfilter_endpoint(page: Page):
#     web_service_url = os.getenv("WEB_SERVICE_URL")
#     page = setup_basic_auth(page)
#     response = page.goto(f"{web_service_url}ipfilter")

#     assert response.status == 200
#     assert response.text() == "ok"


# def test_ipfilter_basic_auth_endpoint(page: Page):
#     web_service_url = os.getenv("WEB_SERVICE_URL")
#     response = page.goto(f"{web_service_url}ipfilter-basic-auth")
#     assert response.status == 401
#     assert response.headers["www-authenticate"] == 'Basic realm="Login Required"'

#     page = setup_basic_auth(page)

#     response = page.goto(f"{web_service_url}ipfilter-basic-auth")

#     assert response.status == 200
#     assert response.text() == "ok"
