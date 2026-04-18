"""automationexercise.com landing page."""
from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class HomePage(BasePage):
    url_path = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.logo = page.get_by_role("img", name="Website for automation practice")
        self.nav_signup_login = page.get_by_role("link", name="Signup / Login")
        self.nav_home = page.get_by_role("link", name="Home").first
        self.nav_products = page.get_by_role("link", name="Products")
        self.nav_cart = page.get_by_role("link", name="Cart").first
        self.nav_contact = page.get_by_role("link", name="Contact us")
        self.logged_in_label = page.locator("a", has_text="Logged in as")

    def open(self) -> "HomePage":
        self.navigate()
        return self

    def go_to_login(self) -> None:
        self.click_element(self.nav_signup_login)
