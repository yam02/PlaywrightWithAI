"""Full account-creation flow: New User Signup -> Enter Account Info -> Account Created."""
from __future__ import annotations

from typing import TypedDict

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SignupUser(TypedDict, total=False):
    name: str
    email: str
    password: str
    dob_day: str
    dob_month: str
    dob_year: str
    first_name: str
    last_name: str
    company: str
    address: str
    address2: str
    country: str
    state: str
    city: str
    zipcode: str
    mobile: str


class SignupPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.signup_name = page.locator('input[data-qa="signup-name"]')
        self.signup_email = page.locator('input[data-qa="signup-email"]')
        self.signup_button = page.locator('button[data-qa="signup-button"]')

        self.enter_account_info_heading = page.locator("h2 b", has_text="Enter Account Information")
        self.title_mr = page.locator("#id_gender1")
        self.password = page.locator('input[data-qa="password"]')
        self.days = page.locator('select[data-qa="days"]')
        self.months = page.locator('select[data-qa="months"]')
        self.years = page.locator('select[data-qa="years"]')

        self.first_name = page.locator('input[data-qa="first_name"]')
        self.last_name = page.locator('input[data-qa="last_name"]')
        self.company = page.locator('input[data-qa="company"]')
        self.address1 = page.locator('input[data-qa="address"]')
        self.address2 = page.locator('input[data-qa="address2"]')
        self.country = page.locator('select[data-qa="country"]')
        self.state = page.locator('input[data-qa="state"]')
        self.city = page.locator('input[data-qa="city"]')
        self.zipcode = page.locator('input[data-qa="zipcode"]')
        self.mobile = page.locator('input[data-qa="mobile_number"]')
        self.create_account_btn = page.locator('button[data-qa="create-account"]')

        self.account_created_heading = page.locator('h2[data-qa="account-created"]')
        self.continue_btn = page.locator('a[data-qa="continue-button"]')

    def start(self, name: str, email: str) -> None:
        self.log.info("signup start: name=%s email=%s", name, email)
        self.fill_input(self.signup_name, name)
        self.fill_input(self.signup_email, email)
        self.click_element(self.signup_button)
        expect(self.enter_account_info_heading).to_be_visible()

    def complete(self, user: SignupUser) -> None:
        self.log.info("submitting account info for %s", user.get("email", "<no-email>"))
        self.title_mr.check()
        self.fill_input(self.password, user["password"], sensitive=True)
        self.days.select_option(user["dob_day"])
        self.months.select_option(user["dob_month"])
        self.years.select_option(user["dob_year"])
        self.fill_input(self.first_name, user["first_name"])
        self.fill_input(self.last_name, user["last_name"])
        self.fill_input(self.company, user.get("company", ""))
        self.fill_input(self.address1, user["address"])
        self.fill_input(self.address2, user.get("address2", ""))
        self.country.select_option(user["country"])
        self.fill_input(self.state, user["state"])
        self.fill_input(self.city, user["city"])
        self.fill_input(self.zipcode, user["zipcode"])
        self.fill_input(self.mobile, user["mobile"])
        self.click_element(self.create_account_btn)

    def confirm_and_continue(self) -> None:
        expect(self.account_created_heading).to_be_visible()
        self.log.info("account created, continuing to site")
        self.click_element(self.continue_btn)
