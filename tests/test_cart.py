"""Cart page coverage: quantity aggregation, deletion, quantity read-only behavior."""
from __future__ import annotations

import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.products_page import ProductsPage


@pytest.mark.regression
@pytest.mark.cart
def test_adding_same_product_twice_increases_quantity(
    products_page: ProductsPage,
    cart_page: CartPage,
) -> None:
    products_page.open()
    expected_name = products_page.first_product_name()

    products_page.add_first_result_to_cart()
    products_page.continue_shopping_from_modal()

    products_page.add_first_result_to_cart()
    products_page.go_to_cart_from_modal()

    expect(cart_page.cart_rows).to_have_count(1)
    assert cart_page.product_name_of_first() == expected_name
    assert cart_page.quantity_of_first() == 2


@pytest.mark.regression
@pytest.mark.cart
def test_removing_products_decreases_count_and_empties_cart(
    products_page: ProductsPage,
    cart_page: CartPage,
) -> None:
    products_page.open()
    products_page.add_nth_result_to_cart(0)
    products_page.continue_shopping_from_modal()
    products_page.add_nth_result_to_cart(1)
    products_page.go_to_cart_from_modal()

    expect(cart_page.cart_rows).to_have_count(2)

    cart_page.delete_row(0)
    expect(cart_page.cart_rows).to_have_count(1)

    cart_page.delete_row(0)
    expect(cart_page.empty_cart_message).to_be_visible()
    expect(cart_page.empty_cart_message).to_contain_text("Cart is empty")


@pytest.mark.smoke
@pytest.mark.cart
def test_quantity_is_not_editable_in_cart(
    products_page: ProductsPage,
    cart_page: CartPage,
) -> None:
    products_page.open()
    products_page.add_first_result_to_cart()
    products_page.go_to_cart_from_modal()

    expect(cart_page.cart_rows).to_have_count(1)
    assert cart_page.quantity_of_first() == 1

    assert cart_page.quantity_input_count_of_first() == 0, (
        "cart quantity cell must not contain an editable <input>"
    )
    assert cart_page.quantity_button_has_disabled_class(), (
        "cart quantity button must carry the 'disabled' class"
    )
