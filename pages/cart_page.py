"""Cart page — cart contents, checkout, register/login modal."""
from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class CartPage(BasePage):
    url_path = "/view_cart"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.cart_rows = page.locator("#cart_info_table tbody tr")
        self.empty_cart_message = page.locator("#empty_cart")
        self.proceed_to_checkout_btn = page.locator("a.check_out", has_text="Proceed To Checkout")

        self.checkout_modal = page.locator("#checkoutModal")
        self.modal_register_login_link = page.locator('#checkoutModal a[href="/login"]')

    def open(self) -> "CartPage":
        self.navigate()
        return self

    def item_count(self) -> int:
        return self.cart_rows.count()

    def first_row(self):
        return self.cart_rows.first

    def product_name_of_first(self) -> str:
        name = self.first_row().locator(".cart_description h4 a").text_content() or ""
        return name.strip()

    def quantity_of_first(self) -> int:
        qty = self.first_row().locator(".cart_quantity button").text_content() or "0"
        return int(qty.strip())

    def quantity_element_of_first(self):
        return self.first_row().locator(".cart_quantity button").first

    def quantity_input_count_of_first(self) -> int:
        return self.first_row().locator(".cart_quantity input").count()

    def quantity_button_has_disabled_class(self) -> bool:
        class_attr = self.quantity_element_of_first().get_attribute("class") or ""
        return "disabled" in class_attr.split()

    def delete_row(self, index: int = 0) -> None:
        self.log.info("deleting cart row #%d", index)
        row = self.cart_rows.nth(index)
        delete_link = row.locator("a.cart_quantity_delete").first
        delete_link.scroll_into_view_if_needed()
        self.click_element(delete_link)

    def proceed_to_checkout(self) -> None:
        self.log.info("proceeding to checkout")
        self.click_element(self.proceed_to_checkout_btn)

    def click_register_login_from_modal(self) -> None:
        self.log.info("register/login via checkout modal")
        self.checkout_modal.wait_for(state="visible")
        self.click_element(self.modal_register_login_link)
