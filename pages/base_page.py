"""Shared Playwright interactions for every page object."""
from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect

from config.config import config
from utils.healing import safe_click, safe_fill, safe_hover
from utils.logger import get_logger


class BasePage:
    url_path: str = ""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.log = get_logger(self.__class__.__name__)

    def navigate(self, path: str | None = None) -> None:
        target = path if path is not None else self.url_path
        full = f"{config.base_url}{target}" if target.startswith("/") else target or config.base_url
        self.log.info("Navigating to %s", full)
        self.page.goto(full, wait_until="domcontentloaded")

    def click_element(
        self,
        locator: Locator,
        *,
        key: str | None = None,
        description: str | None = None,
    ) -> None:
        if key and description:
            safe_click(self.page, key, description)
            return
        self.log.debug("click %s", locator)
        locator.click()

    def fill_input(
        self,
        locator: Locator,
        value: str,
        *,
        sensitive: bool = False,
        key: str | None = None,
        description: str | None = None,
    ) -> None:
        if key and description:
            safe_fill(self.page, key, value, description, sensitive=sensitive)
            return
        self.log.debug("fill %s with %s", locator, "***" if sensitive else value)
        locator.fill(value)

    def hover_element(
        self,
        locator: Locator | None = None,
        *,
        key: str | None = None,
        description: str | None = None,
    ) -> None:
        if key and description:
            safe_hover(self.page, key, description)
            return
        if locator is None:
            raise ValueError("hover_element requires either a locator or key+description")
        self.log.debug("hover %s", locator)
        locator.hover()

    def wait_for_selector(self, selector: str, *, state: str = "visible", timeout: int | None = None) -> Locator:
        self.log.debug("wait_for_selector=%s state=%s", selector, state)
        self.page.wait_for_selector(selector, state=state, timeout=timeout)
        return self.page.locator(selector)

    def expect_visible(self, locator: Locator) -> None:
        expect(locator).to_be_visible()

    def expect_text(self, locator: Locator, text: str) -> None:
        expect(locator).to_contain_text(text)

    def expect_url_contains(self, fragment: str) -> None:
        expect(self.page).to_have_url(re.compile(re.escape(fragment)))

    def title(self) -> str:
        return self.page.title()
