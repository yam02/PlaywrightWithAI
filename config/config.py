"""Centralized environment-driven configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)


def _bool(val: str | None, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _int(val: str | None, default: int) -> int:
    try:
        return int(val) if val is not None else default
    except ValueError:
        return default


@dataclass(frozen=True)
class AppConfig:
    base_url: str = os.getenv("BASE_URL", "https://automationexercise.com")
    browser: str = os.getenv("BROWSER", "chromium")
    headless: bool = _bool(os.getenv("HEADLESS"), default=True)
    slow_mo: int = _int(os.getenv("SLOW_MO"), default=0)
    default_timeout: int = _int(os.getenv("DEFAULT_TIMEOUT"), default=30_000)
    viewport_width: int = _int(os.getenv("VIEWPORT_WIDTH"), default=1440)
    viewport_height: int = _int(os.getenv("VIEWPORT_HEIGHT"), default=900)

    test_user_name: str = os.getenv("TEST_USER_NAME", "TestUserYam")
    test_user_email: str = os.getenv("TEST_USER_EMAIL", "yamunagoodigood@gmail.com")


config = AppConfig()
