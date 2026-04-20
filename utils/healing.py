"""Self-healing Playwright actions — primary -> cached fallbacks -> AI suggestions."""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import List, Optional

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from utils.ai_client import get_healer
from utils.logger import get_logger

log = get_logger("healing")

_STORE_PATH = Path(__file__).resolve().parent.parent / "locator_store.json"
_PROBE_TIMEOUT_MS = 4_000
_MAX_AI_CANDIDATES = 6

_HEALABLE_SIGNALS = (
    "not clickable",
    "not visible",
    "not stable",
    "subtree intercepted",
    "not enabled",
    "outside of the viewport",
    "strict mode violation",
    "element is not attached",
    "no element matches selector",
    "waiting for selector",
    "waiting for locator",
    "element is not an <input>",
)


def _is_healable(exc: BaseException) -> bool:
    if isinstance(exc, PlaywrightTimeoutError):
        return True
    if isinstance(exc, PlaywrightError):
        msg = str(exc).lower()
        return any(signal in msg for signal in _HEALABLE_SIGNALS)
    return False


class LocatorStore:
    """Thread-safe JSON-backed registry of primary selectors + healed fallbacks."""

    _instance: Optional["LocatorStore"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "LocatorStore":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_store()
        return cls._instance

    def _init_store(self) -> None:
        self._path = _STORE_PATH
        self._data: dict = {}
        self._reload()

    def _reload(self) -> None:
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                log.error("locator_store.json malformed: %s — starting empty.", exc)
                self._data = {}
        else:
            self._data = {}

    def _persist(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")

    def entry(self, key: str) -> Optional[dict]:
        return self._data.get(key)

    def candidates(self, key: str) -> List[str]:
        entry = self._data.get(key)
        if not entry:
            return []
        seen: list[str] = []
        for sel in [entry.get("primary"), *entry.get("healed", [])]:
            if sel and sel not in seen:
                seen.append(sel)
        return seen

    def description(self, key: str) -> str:
        entry = self._data.get(key)
        return (entry or {}).get("description", "")

    def register(self, key: str, description: str, primary: str) -> None:
        with self._lock:
            if key not in self._data:
                self._data[key] = {"description": description, "primary": primary, "healed": []}
                self._persist()

    def promote(self, key: str, selector: str) -> None:
        with self._lock:
            entry = self._data.setdefault(
                key, {"description": "", "primary": selector, "healed": []}
            )
            healed = entry.setdefault("healed", [])
            if selector == entry.get("primary"):
                return
            if selector in healed:
                healed.remove(selector)
            healed.insert(0, selector)
            entry["healed"] = healed[:10]
            self._persist()
            log.info("Promoted selector for '%s': %s", key, selector)


def _probe(page: Page, selector: str) -> bool:
    """Return True if selector resolves to at least one attached element quickly."""
    try:
        return page.locator(selector).first.count() > 0
    except Exception as exc:  # noqa: BLE001
        log.debug("Probe failed for %s: %s", selector, exc)
        return False


def _run_action(page: Page, selector: str, action: str, *, value: Optional[str] = None) -> None:
    loc = page.locator(selector).first
    if action == "click":
        loc.click(timeout=_PROBE_TIMEOUT_MS)
    elif action == "fill":
        if value is None:
            raise ValueError("fill action requires a value")
        loc.fill(value, timeout=_PROBE_TIMEOUT_MS)
    elif action == "hover":
        loc.hover(timeout=_PROBE_TIMEOUT_MS)
    else:
        raise ValueError(f"Unsupported action: {action}")


def _ai_suggestions(page: Page, description: str, tried: List[str]) -> List[str]:
    healer = get_healer()
    if not healer.enabled:
        return []
    try:
        dom = page.content()
    except Exception as exc:  # noqa: BLE001
        log.warning("Could not capture DOM for AI healer: %s", exc)
        return []
    raw = healer.suggest(description=description, dom=dom, exclude=tried)
    return raw[:_MAX_AI_CANDIDATES]


def _heal_and_act(
    page: Page,
    key: str,
    description: str,
    action: str,
    *,
    value: Optional[str] = None,
    sensitive: bool = False,
) -> None:
    store = LocatorStore()
    if description:
        existing = store.entry(key)
        if not existing or not existing.get("description"):
            candidates_now = store.candidates(key)
            if candidates_now:
                store.register(key, description, candidates_now[0])

    candidates = store.candidates(key)
    tried: list[str] = []
    last_exc: Optional[BaseException] = None

    for sel in candidates:
        tried.append(sel)
        printable_val = "***" if sensitive else value
        log.debug("try %s on '%s' via %s (value=%s)", action, key, sel, printable_val)
        try:
            _run_action(page, sel, action, value=value)
            if sel != candidates[0]:
                store.promote(key, sel)
            return
        except Exception as exc:  # noqa: BLE001
            if not _is_healable(exc):
                raise
            log.warning("Selector failed (healable) for '%s': %s -- %s", key, sel, exc)
            last_exc = exc

    log.info("All cached selectors failed for '%s'; requesting AI suggestions.", key)
    for sel in _ai_suggestions(page, description or store.description(key), tried):
        if sel in tried:
            continue
        tried.append(sel)
        if not _probe(page, sel):
            log.debug("AI candidate %s did not resolve; skipping.", sel)
            continue
        try:
            _run_action(page, sel, action, value=value)
            store.promote(key, sel)
            log.info("AI-suggested selector succeeded for '%s': %s", key, sel)
            return
        except Exception as exc:  # noqa: BLE001
            if not _is_healable(exc):
                raise
            log.warning("AI candidate failed for '%s': %s -- %s", key, sel, exc)
            last_exc = exc

    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"No selectors registered for '{key}' and AI healing produced none.")


def safe_click(page: Page, key: str, description: str = "") -> None:
    _heal_and_act(page, key, description, "click")


def safe_fill(page: Page, key: str, value: str, description: str = "", *, sensitive: bool = False) -> None:
    _heal_and_act(page, key, description, "fill", value=value, sensitive=sensitive)


def safe_hover(page: Page, key: str, description: str = "") -> None:
    _heal_and_act(page, key, description, "hover")
