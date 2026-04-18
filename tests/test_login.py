"""Login flow smoke tests against automationexercise.com."""
from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from config.config import config
from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.login
def test_login_page_is_reachable_from_home(home_page: HomePage, login_page: LoginPage) -> None:
    home_page.open()
    expect(home_page.nav_signup_login).to_be_visible()

    home_page.go_to_login()

    expect(login_page.login_heading).to_be_visible()
    expect(login_page.signup_heading).to_be_visible()
    expect(login_page.page).to_have_url(re.compile(r"/login"))


@pytest.mark.smoke
@pytest.mark.login
def test_login_form_fields_are_rendered(login_page: LoginPage) -> None:
    login_page.open()

    expect(login_page.login_email).to_be_visible()
    expect(login_page.login_email).to_be_editable()
    expect(login_page.login_password).to_be_visible()
    expect(login_page.login_password).to_be_editable()
    expect(login_page.login_button).to_be_enabled()


@pytest.mark.login
def test_login_with_invalid_credentials_shows_error(login_page: LoginPage) -> None:
    login_page.open()
    login_page.login(email=config.test_user_email, password="definitely-not-the-right-password")

    expect(login_page.login_error).to_be_visible()
