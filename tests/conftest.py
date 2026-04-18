"""Page-object fixtures scoped to the tests package."""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.fixture()
def home_page(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture()
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)
