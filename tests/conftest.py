"""Page-object fixtures scoped to the tests package."""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.payment_page import PaymentPage
from pages.product_details_page import ProductDetailsPage
from pages.products_page import ProductsPage
from pages.signup_page import SignupPage


@pytest.fixture()
def home_page(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture()
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture()
def products_page(page: Page) -> ProductsPage:
    return ProductsPage(page)


@pytest.fixture()
def product_details_page(page: Page) -> ProductDetailsPage:
    return ProductDetailsPage(page)


@pytest.fixture()
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture()
def signup_page(page: Page) -> SignupPage:
    return SignupPage(page)


@pytest.fixture()
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)


@pytest.fixture()
def payment_page(page: Page) -> PaymentPage:
    return PaymentPage(page)
