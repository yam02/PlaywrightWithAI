"""Payment page — card details and order confirmation."""
from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class PaymentPage(BasePage):
    url_path = "/payment"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.name_on_card = page.locator('input[data-qa="name-on-card"]')
        self.card_number = page.locator('input[data-qa="card-number"]')
        self.cvc = page.locator('input[data-qa="cvc"]')
        self.expiry_month = page.locator('input[data-qa="expiry-month"]')
        self.expiry_year = page.locator('input[data-qa="expiry-year"]')
        self.pay_button = page.locator('button[data-qa="pay-button"]')
        self.order_confirmed_message = page.get_by_text(
            "Congratulations! Your order has been confirmed!"
        )

    def wait_for_load(self) -> None:
        self.page.wait_for_url("**/payment")

    def pay(
        self,
        cardholder: str,
        *,
        card_number: str = "4111111111111111",
        cvc: str = "123",
        month: str = "12",
        year: str = "2030",
    ) -> None:
        self.log.info("submitting payment as %s (card ****%s)", cardholder, card_number[-4:])
        self.fill_input(self.name_on_card, cardholder)
        self.fill_input(self.card_number, card_number, sensitive=True)
        self.fill_input(self.cvc, cvc, sensitive=True)
        self.fill_input(self.expiry_month, month)
        self.fill_input(self.expiry_year, year)
        self.click_element(self.pay_button)
