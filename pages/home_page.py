"""automationexercise.com landing page."""
from __future__ import annotations

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class HomePage(BasePage):
    url_path = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.logo = page.get_by_role("img", name="Website for automation practice")
        self.nav_signup_login = page.get_by_role("link", name="Signup / Login").first
        self.nav_home = page.get_by_role("link", name="Home").first
        self.nav_products = page.get_by_role("link", name="Products").first
        self.nav_cart = page.get_by_role("link", name="Cart").first
        self.nav_contact = page.get_by_role("link", name="Contact us").first
        self.nav_test_cases = page.get_by_role("link", name="Test Cases").first
        self.nav_api_testing = page.get_by_role("link", name="API Testing").first
        self.logged_in_label = page.locator("a", has_text="Logged in as")
        self.delete_account_link = page.get_by_role("link", name="Delete Account")
        self.account_deleted_heading = page.locator('h2[data-qa="account-deleted"]')

        self.nav_links: dict[str, Locator] = {
            "Home": self.nav_home,
            "Products": self.nav_products,
            "Cart": self.nav_cart,
            "Signup / Login": self.nav_signup_login,
            "Test Cases": self.nav_test_cases,
            "API Testing": self.nav_api_testing,
            "Contact us": self.nav_contact,
        }

        self.category_women_toggle = page.locator('a[href="#Women"]')
        self.category_men_toggle = page.locator('a[href="#Men"]')
        self.category_kids_toggle = page.locator('a[href="#Kids"]')
        self.brands_panel = page.locator(".brands_products")

        self.scroll_to_top_button = page.locator("#scrollUp")

    def open(self) -> "HomePage":
        self.navigate()
        return self

    def go_to_login(self) -> None:
        self.log.info("navigating to Signup / Login")
        self.click_element(self.nav_signup_login)

    def click_header_link(self, name: str) -> None:
        self.log.info("header nav click: %s", name)
        link = self.nav_links.get(name)
        if link is None:
            raise KeyError(f"Unknown header nav link: {name!r}")
        self.click_element(link)

    def current_path(self) -> str:
        from urllib.parse import urlparse

        path = urlparse(self.page.url).path.rstrip("/")
        return path or "/"

    def expand_category(self, name: str) -> None:
        self.click_element(self.page.locator(f'a[href="#{name}"]'))

    def click_category_subitem(self, category: str, subitem: str) -> None:
        self.expand_category(category)
        self.click_element(self.page.get_by_role("link", name=subitem).first)

    def click_brand(self, brand: str) -> None:
        link = self.brands_panel.locator(f'a[href^="/brand_products/{brand}"]').first
        link.scroll_into_view_if_needed()
        self.click_element(link)

    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def click_scroll_to_top(self) -> None:
        self.scroll_to_top_button.wait_for(state="visible")
        self.click_element(self.scroll_to_top_button)

    def scroll_y(self) -> int:
        return int(self.page.evaluate("window.scrollY"))

    def wait_for_scrolled_to_top(self, threshold: int = 5) -> None:
        self.page.wait_for_function(f"window.scrollY < {threshold}")

    def delete_account(self) -> None:
        self.log.info("deleting account")
        self.click_element(self.delete_account_link)
