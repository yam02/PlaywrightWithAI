"""Signup / Login page — contains both the login and the new-user signup forms."""
from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    url_path = "/login"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.login_heading = page.get_by_role("heading", name="Login to your account")
        self.login_email = page.locator('input[data-qa="login-email"]')
        self.login_password = page.locator('input[data-qa="login-password"]')
        self.login_button = page.locator('button[data-qa="login-button"]')
        self.login_error = page.get_by_text("Your email or password is incorrect!")

        self.signup_heading = page.get_by_role("heading", name="New User Signup!")
        self.signup_name = page.locator('input[data-qa="signup-name"]')
        self.signup_email = page.locator('input[data-qa="signup-email"]')
        self.signup_button = page.locator('button[data-qa="signup-button"]')
        self.signup_email_exists_error = page.get_by_text("Email Address already exist!")

    def open(self) -> "LoginPage":
        self.navigate()
        return self

    def login(self, email: str, password: str) -> None:
        self.fill_input(self.login_email, email)
        self.fill_input(self.login_password, password, sensitive=True)
        self.click_element(self.login_button)

    def start_signup(self, name: str, email: str) -> None:
        self.fill_input(self.signup_name, name)
        self.fill_input(self.signup_email, email)
        self.click_element(self.signup_button)
