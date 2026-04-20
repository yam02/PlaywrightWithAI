"""Checkout page — address review, order review, place-order handoff to payment."""
from __future__ import annotations

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    url_path = "/checkout"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.address_details_heading = page.locator("h2", has_text="Address Details")
        self.review_order_heading = page.locator("h2", has_text="Review Your Order")
        self.comment_textarea = page.locator('textarea[name="message"]')
        self.place_order_btn = page.locator("a.check_out", has_text="Place Order")

    def wait_for_load(self) -> None:
        self.page.wait_for_url("**/checkout")
        expect(self.address_details_heading).to_be_visible()
        expect(self.review_order_heading).to_be_visible()

    def add_comment(self, comment: str) -> None:
        self.log.info("adding order comment (%d chars)", len(comment))
        self.fill_input(self.comment_textarea, comment)

    def place_order(self) -> None:
        self.log.info("placing order")
        self.click_element(self.place_order_btn)
