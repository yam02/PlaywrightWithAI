"""Global pytest fixtures — browser lifecycle, page injection, artifacts on failure."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config.config import config
from utils.logger import get_logger

log = get_logger("conftest")

ARTIFACTS_DIR = Path(__file__).resolve().parent / "reports" / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

SCREENSHOTS_DIR = Path(__file__).resolve().parent / "results" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--browser-name",
        action="store",
        default=None,
        help="Override browser: chromium | firefox | webkit",
    )
    parser.addoption(
        "--slow-mo",
        action="store",
        type=int,
        default=None,
        help="Milliseconds to pause between Playwright actions",
    )


@pytest.fixture(scope="session")
def playwright() -> Iterator[Playwright]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(request: pytest.FixtureRequest, playwright: Playwright) -> Iterator[Browser]:
    name = request.config.getoption("--browser-name") or config.browser
    headless = config.headless and not request.config.getoption("--headed")
    slow_mo = request.config.getoption("--slow-mo")
    slow_mo = slow_mo if slow_mo is not None else config.slow_mo

    log.info("Launching %s (headless=%s, slow_mo=%sms)", name, headless, slow_mo)
    launcher = getattr(playwright, name)
    browser = launcher.launch(headless=headless, slow_mo=slow_mo)
    yield browser
    browser.close()


@pytest.fixture()
def context(browser: Browser, request: pytest.FixtureRequest) -> Iterator[BrowserContext]:
    test_name = request.node.name
    ctx = browser.new_context(
        viewport={"width": config.viewport_width, "height": config.viewport_height},
        record_video_dir=str(ARTIFACTS_DIR / "videos"),
        base_url=config.base_url,
    )
    ctx.set_default_timeout(config.default_timeout)
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield ctx

    trace_path = ARTIFACTS_DIR / f"trace-{test_name}.zip"
    ctx.tracing.stop(path=str(trace_path))
    ctx.close()


@pytest.fixture()
def page(context: BrowserContext, request: pytest.FixtureRequest) -> Iterator[Page]:
    p = context.new_page()
    yield p

    rep_call = getattr(request.node, "rep_call", None)
    if rep_call is not None and rep_call.failed:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", request.node.name)
        shot = SCREENSHOTS_DIR / f"{safe_name}-{stamp}.png"
        try:
            p.screenshot(path=str(shot), full_page=True)
            log.error("Screenshot saved: %s", shot)
        except Exception as exc:
            log.warning("Screenshot failed: %s", exc)
    p.close()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item):
    """Expose the result of each phase (setup/call/teardown) on the item for fixtures."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
