"""Home-page coverage: header nav, e2e checkout, cart-through-signup, sidebar filter, scroll-to-top."""
from __future__ import annotations

import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.payment_page import PaymentPage
from pages.products_page import ProductsPage
from pages.signup_page import SignupPage
from utils.test_data import unique_user


@pytest.mark.smoke
@pytest.mark.home
@pytest.mark.parametrize(
    "link_name, expected_path",
    [
        ("Home", "/"),
        ("Products", "/products"),
        ("Cart", "/view_cart"),
        ("Signup / Login", "/login"),
        ("Test Cases", "/test_cases"),
        ("API Testing", "/api_list"),
        ("Contact us", "/contact_us"),
    ],
)
def test_header_menu_navigates(home_page: HomePage, link_name: str, expected_path: str) -> None:
    home_page.open()
    home_page.click_header_link(link_name)
    expected = expected_path.rstrip("/") or "/"
    assert home_page.current_path() == expected, (
        f"got path {home_page.current_path()!r}, expected {expected!r}"
    )


@pytest.mark.regression
@pytest.mark.home
def test_search_add_to_cart_login_checkout(
    home_page: HomePage,
    products_page: ProductsPage,
    cart_page: CartPage,
    signup_page: SignupPage,
    checkout_page: CheckoutPage,
    payment_page: PaymentPage,
) -> None:
    user = unique_user()

    home_page.open()
    home_page.go_to_login()
    signup_page.start(user["name"], user["email"])
    signup_page.complete(user)
    signup_page.confirm_and_continue()
    expect(home_page.logged_in_label).to_be_visible()

    products_page.open()
    products_page.search("top")
    expect(products_page.searched_products_heading).to_be_visible()
    expect(products_page.product_cards.first).to_be_visible()

    products_page.add_first_result_to_cart()
    products_page.go_to_cart_from_modal()
    expect(cart_page.cart_rows).to_have_count(1)

    cart_page.proceed_to_checkout()
    checkout_page.wait_for_load()
    checkout_page.add_comment("Placed by Playwright e2e")
    checkout_page.place_order()

    payment_page.wait_for_load()
    payment_page.pay(user["name"])
    expect(payment_page.order_confirmed_message).to_be_visible()

    home_page.delete_account()
    expect(home_page.account_deleted_heading).to_be_visible()


@pytest.mark.regression
@pytest.mark.home
def test_cart_persists_through_signup(
    home_page: HomePage,
    products_page: ProductsPage,
    cart_page: CartPage,
    signup_page: SignupPage,
) -> None:
    user = unique_user()

    home_page.open()
    products_page.open()
    products_page.add_first_result_to_cart()
    products_page.go_to_cart_from_modal()
    assert cart_page.item_count() == 1

    cart_page.proceed_to_checkout()
    cart_page.click_register_login_from_modal()

    signup_page.start(user["name"], user["email"])
    signup_page.complete(user)
    signup_page.confirm_and_continue()
    expect(home_page.logged_in_label).to_be_visible()

    home_page.click_header_link("Cart")
    expect(cart_page.cart_rows).to_have_count(1)

    home_page.delete_account()
    expect(home_page.account_deleted_heading).to_be_visible()


@pytest.mark.smoke
@pytest.mark.home
@pytest.mark.parametrize(
    "kind, args, expected_fragment",
    [
        ("category", ("Women", "Dress"), "/category_products/"),
        ("category", ("Men", "Tshirts"), "/category_products/"),
        ("brand", ("Polo",), "/brand_products/"),
        ("brand", ("H&M",), "/brand_products/"),
    ],
)
def test_sidebar_filter_navigates_to_products(
    home_page: HomePage,
    kind: str,
    args: tuple,
    expected_fragment: str,
) -> None:
    home_page.open()
    if kind == "category":
        category, subitem = args
        home_page.click_category_subitem(category, subitem)
    else:
        (brand,) = args
        home_page.click_brand(brand)

    assert expected_fragment in home_page.page.url, (
        f"expected url containing {expected_fragment!r}, got {home_page.page.url!r}"
    )


@pytest.mark.smoke
@pytest.mark.home
def test_go_to_top(home_page: HomePage) -> None:
    home_page.open()
    home_page.scroll_to_bottom()
    expect(home_page.scroll_to_top_button).to_be_visible()

    home_page.click_scroll_to_top()
    home_page.wait_for_scrolled_to_top()
    assert home_page.scroll_y() < 5
