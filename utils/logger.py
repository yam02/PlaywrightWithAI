"""Shared logger factory — one configured logger per module.

Run-scoped layout:
    results/run-<YYYYMMDD-HHMMSS>/
        run.log            <- DEBUG+ full detail
        screenshots/       <- failure artifacts, same folder as the log

Level policy:
    INFO   -- meaningful test-flow milestones (login attempt, place order, delete account)
    DEBUG  -- low-level mechanics (clicks, fills, locator attempts, healer probes)
    WARN+  -- recoverable problems (healing triggered, screenshot failed)
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_RESULTS_ROOT = PROJECT_ROOT / "results"
_RUN_ENV_KEY = "PW_RUN_DIR"


def _resolve_run_dir() -> Path:
    existing = os.environ.get(_RUN_ENV_KEY)
    if existing:
        return Path(existing)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = _RESULTS_ROOT / f"run-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "screenshots").mkdir(exist_ok=True)
    os.environ[_RUN_ENV_KEY] = str(run_dir)
    return run_dir


RUN_DIR = _resolve_run_dir()
SCREENSHOTS_DIR = RUN_DIR / "screenshots"
_LOG_FILE = RUN_DIR / "run.log"

_FORMAT = "%(asctime)s [%(levelname)8s] %(name)s :: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_configured = False


def _configure_root() -> None:
    global _configured
    if _configured:
        return

    formatter = logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT)

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.INFO)
    stream.setFormatter(formatter)

    root = logging.getLogger("framework")
    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    root.addHandler(stream)
    root.propagate = False

    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure_root()
    return logging.getLogger(f"framework.{name}")
