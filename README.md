# Playwright + Pytest Web Automation Framework

Enterprise-style web automation framework for [automationexercise.com](https://automationexercise.com/) built on Python + Playwright + Pytest, following the Page Object Model.

## Layout

```
.
├── config/              # env-driven settings (AppConfig dataclass)
├── pages/               # Page Object classes (BasePage + page classes)
├── tests/               # Pytest test modules
├── utils/               # logger and other helpers
├── conftest.py          # global fixtures: playwright, browser, context, page
├── pytest.ini           # pytest configuration + HTML report
├── requirements.txt
├── .env.example         # copy to .env and adjust
└── reports/             # generated (html report, traces, screenshots, videos)
```

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
playwright install            # download browser binaries
cp .env.example .env          # then edit as needed
```

## Running tests

Headless (default):
```bash
pytest
```

Headed:
```bash
pytest --headed
```

Pick a browser:
```bash
pytest --browser-name chromium
pytest --browser-name firefox
pytest --browser-name webkit
```

Slow-mo for debugging (ms between actions):
```bash
pytest --headed --slow-mo 300
```

Run by marker:
```bash
pytest -m smoke
pytest -m "login and not regression"
```

Parallel execution (pytest-xdist):
```bash
pytest -n auto
```

## Reports

HTML report is generated automatically at `reports/report.html`:
```bash
pytest
start reports/report.html     # Windows
open reports/report.html      # macOS
```

Allure (optional):
```bash
pytest --alluredir=allure-results
allure serve allure-results
```

Playwright trace viewer (written per test to `reports/artifacts/trace-<test>.zip`):
```bash
playwright show-trace reports/artifacts/trace-test_login_page_is_reachable_from_home.zip
```

Screenshots on failure land in `reports/artifacts/`; videos land in `reports/artifacts/videos/`.

## Environment variables

| Variable          | Default                          | Purpose                    |
|-------------------|----------------------------------|----------------------------|
| `BASE_URL`        | `https://automationexercise.com` | Target environment         |
| `BROWSER`         | `chromium`                       | chromium / firefox / webkit|
| `HEADLESS`        | `true`                           | Headless mode              |
| `SLOW_MO`         | `0`                              | ms between actions         |
| `DEFAULT_TIMEOUT` | `30000`                          | ms — Playwright default    |
| `TEST_USER_NAME`  | `TestUserYam`                    | Signup test name           |
| `TEST_USER_EMAIL` | `yamunagoodigood@gmail.com`      | Signup/login test email    |

CLI flags (`--headed`, `--browser-name`, `--slow-mo`) override env vars for a single run.

## Adding a new page

1. Create `pages/<your_page>.py` with a class that inherits [BasePage](pages/base_page.py).
2. Declare locators in `__init__` using `page.get_by_role`, `page.get_by_text`, or `page.locator(...)`.
3. Expose business-flow methods (e.g., `add_to_cart`, `submit_order`) — never leak raw locators to tests.
4. Register a fixture in [tests/conftest.py](tests/conftest.py) and write your test.

## Conventions

- **Web-first assertions only**: use `expect(locator).to_be_visible()` instead of boolean checks. They auto-retry up to the configured timeout.
- **Role-based locators first**: prefer `get_by_role`, `get_by_label`, `get_by_text` over CSS/XPath.
- **No `time.sleep`**: rely on Playwright's auto-waiting and `expect` retries.
- **No hardcoded URLs in tests**: navigate through page objects; URL paths live on the page class.
