"""Products page coverage: search, view + add, write review."""
from __future__ import annotations

import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.product_details_page import ProductDetailsPage
from pages.products_page import ProductsPage
from utils.test_data import unique_reviewer


@pytest.mark.smoke
@pytest.mark.products
@pytest.mark.parametrize("term", ["top", "dress", "jeans"])
def test_search_shows_matching_results(products_page: ProductsPage, term: str) -> None:
    products_page.open()
    products_page.search(term)

    expect(products_page.searched_products_heading).to_be_visible()
    expect(products_page.product_cards.first).to_be_visible()
    assert products_page.result_count() > 0

    names = products_page.product_names()
    assert any(term.lower() in n.lower() for n in names), (
        f"no result in {names!r} contained {term!r}"
    )


@pytest.mark.smoke
@pytest.mark.products
def test_search_view_product_and_add_to_cart(
    products_page: ProductsPage,
    product_details_page: ProductDetailsPage,
    cart_page: CartPage,
) -> None:
    products_page.open()
    products_page.search("top")
    expect(products_page.searched_products_heading).to_be_visible()

    expected_name = products_page.first_product_name()
    products_page.open_first_result()

    product_details_page.wait_for_load()
    detail_name = product_details_page.get_name()
    assert detail_name == expected_name, (
        f"details page shows {detail_name!r}, expected {expected_name!r}"
    )

    product_details_page.add_to_cart()
    product_details_page.go_to_cart_from_modal()

    expect(cart_page.cart_rows).to_have_count(1)
    assert cart_page.product_name_of_first() == expected_name


@pytest.mark.regression
@pytest.mark.products
def test_write_product_review(
    products_page: ProductsPage,
    product_details_page: ProductDetailsPage,
) -> None:
    products_page.open()
    products_page.open_first_result()
    product_details_page.wait_for_load()

    reviewer = unique_reviewer()
    product_details_page.write_review(
        name=reviewer["name"],
        email=reviewer["email"],
        review="Great product, loved the quality and fit!",
    )
    expect(product_details_page.review_success).to_be_visible()
