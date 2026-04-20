"""Products listing page — search, product cards, add-to-cart."""
from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class ProductsPage(BasePage):
    url_path = "/products"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.search_input = page.locator("#search_product")
        self.search_button = page.locator("#submit_search")
        self.product_cards = page.locator(".features_items .product-image-wrapper")
        self.searched_products_heading = page.locator("h2.title", has_text="Searched Products")
        self.all_products_heading = page.locator("h2.title", has_text="All Products")

        self.cart_modal = page.locator("#cartModal")
        self.modal_view_cart_link = page.locator('#cartModal a[href="/view_cart"]')
        self.modal_continue_shopping = page.locator("#cartModal .btn.close-modal")

    def open(self) -> "ProductsPage":
        self.navigate()
        return self

    def search(self, term: str) -> None:
        self.log.info("searching products for %r", term)
        self.fill_input(self.search_input, term)
        self.click_element(self.search_button)

    def add_first_result_to_cart(self) -> None:
        self.add_nth_result_to_cart(0)

    def add_nth_result_to_cart(self, index: int) -> None:
        self.log.info("adding product #%d from listing to cart", index)
        card = self.product_cards.nth(index)
        card.scroll_into_view_if_needed()
        card.hover()
        card.locator(".add-to-cart").first.click()
        self.cart_modal.wait_for(state="visible")

    def open_first_result(self) -> None:
        self.log.info("opening first product details page")
        first_card = self.product_cards.first
        first_card.scroll_into_view_if_needed()
        first_card.locator('a[href^="/product_details/"]').first.click()

    def result_count(self) -> int:
        return self.product_cards.count()

    def product_names(self) -> list[str]:
        return self.product_cards.locator(".productinfo p").all_inner_texts()

    def first_product_name(self) -> str:
        return (
            self.product_cards.first.locator(".productinfo p").first.text_content() or ""
        ).strip()

    def go_to_cart_from_modal(self) -> None:
        self.click_element(self.modal_view_cart_link)

    def continue_shopping_from_modal(self) -> None:
        self.click_element(self.modal_continue_shopping)
        self.cart_modal.wait_for(state="hidden")
