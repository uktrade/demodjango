import re
from playwright.sync_api import Page, expect


DEV_ENVIRONMENT_URL = "https://v2.demodjango.dev.uktrade.digital/"
PAGE_TITLE = "DemoDjango"


def test_has_title(page: Page):
    page.goto(DEV_ENVIRONMENT_URL)

    expect(page).to_have_title(re.compile(PAGE_TITLE))
