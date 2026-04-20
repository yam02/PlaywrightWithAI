"""Product details page — product info, quantity, add-to-cart, write review."""
from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ProductDetailsPage(BasePage):
    url_pattern = re.compile(r"/product_details/\d+")

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.product_info = page.locator(".product-information")
        self.product_name = self.product_info.locator("h2").first
        self.product_price = self.product_info.locator("span > span").first
        self.availability_row = self.product_info.locator("p", has_text="Availability")
        self.quantity_input = page.locator("#quantity")
        self.add_to_cart_btn = page.locator("button.cart")

        self.cart_modal = page.locator("#cartModal")
        self.modal_view_cart = page.locator('#cartModal a[href="/view_cart"]')
        self.modal_continue_shopping = page.locator("#cartModal .btn.close-modal")

        self.review_tab = page.locator('a[href="#reviews"]')
        self.review_name = page.locator("#name")
        self.review_email = page.locator("#email")
        self.review_text = page.locator("#review")
        self.submit_review_btn = page.locator("#button-review")
        self.review_success = page.get_by_text("Thank you for your review.")

    def wait_for_load(self) -> None:
        self.page.wait_for_url(self.url_pattern)
        expect(self.product_name).to_be_visible()

    def get_name(self) -> str:
        return (self.product_name.text_content() or "").strip()

    def set_quantity(self, qty: int) -> None:
        self.quantity_input.fill(str(qty))

    def add_to_cart(self) -> None:
        self.log.info("adding to cart from details: %s", self.get_name())
        self.click_element(self.add_to_cart_btn)
        self.cart_modal.wait_for(state="visible")

    def go_to_cart_from_modal(self) -> None:
        self.click_element(self.modal_view_cart)

    def continue_shopping_from_modal(self) -> None:
        self.click_element(self.modal_continue_shopping)
        self.cart_modal.wait_for(state="hidden")

    def write_review(self, name: str, email: str, review: str) -> None:
        self.log.info("submitting review for %s (reviewer=%s)", self.get_name(), email)
        self.review_tab.scroll_into_view_if_needed()
        self.click_element(self.review_tab)
        self.fill_input(self.review_name, name)
        self.fill_input(self.review_email, email)
        self.fill_input(self.review_text, review)
        self.click_element(self.submit_review_btn)
