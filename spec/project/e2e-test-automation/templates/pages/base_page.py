"""Base page object with helpers shared by every page object.

Reference profile: Selenium + pytest. This file is the conformance baseline
for the `spec/project/e2e-test-automation/` core requirements on page-object
encapsulation, deterministic waiting, and the locator hierarchy.

Adapt the marked spots to your application:
  * LOADING_INDICATOR — the test hook your app renders while a page loads
  * PAGE_TITLE / ERROR_DISPLAY — your app's standard page-title / error hooks
  * close_dropdown / clear_and_fill — tuned here for a React + Material-UI
    front end; adjust to your component library.
Everything else is domain-agnostic and can be used as-is.
"""

from __future__ import annotations

import time
from pathlib import Path

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = 15

# ── Application-wide test hooks (adapt to your app) ───────────────────────────
# A dedicated test hook the app renders while a page is loading; waited on by
# wait_for_loading_complete() so tests never race the spinner.
LOADING_INDICATOR = (By.CSS_SELECTOR, "[data-testid='loading-skeleton']")
PAGE_TITLE = (By.CSS_SELECTOR, "[data-testid='page-title']")
ERROR_DISPLAY = (By.CSS_SELECTOR, "[data-testid='error-display']")


class BasePage:
    """Shared helpers inherited by every page object.

    Tests interact only through page-object methods; raw `find_element` calls
    live here and in subclasses, never in test bodies (see the spec's
    page-object-encapsulation requirement).
    """

    def __init__(self, driver: WebDriver, base_url: str) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    # ── Navigation ────────────────────────────────────────────────────────

    def navigate(self, path: str) -> None:
        """Navigate to *path* relative to the base URL."""
        self.driver.get(f"{self.base_url}{path}")

    # ── Waits (condition-based — never time.sleep in a test) ──────────────

    def wait_for_element(
        self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT
    ) -> WebElement:
        """Wait until an element is present in the DOM and return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def wait_for_element_visible(
        self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT
    ) -> WebElement:
        """Wait until an element is visible and return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_element_clickable(
        self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT
    ) -> WebElement:
        """Wait until an element is clickable and return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_element_hidden(
        self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT
    ) -> None:
        """Wait until an element is no longer visible (e.g. a dialog fade-out)."""
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(locator)
        )

    def wait_for_loading_complete(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Wait until the loading indicator disappears."""
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(LOADING_INDICATOR)
        )

    def wait_for_url_contains(
        self, fragment: str, timeout: int = DEFAULT_TIMEOUT
    ) -> None:
        """Wait until the current URL contains *fragment*."""
        WebDriverWait(self.driver, timeout).until(EC.url_contains(fragment))

    # ── Queries ───────────────────────────────────────────────────────────

    def find_by_testid(self, testid: str) -> WebElement:
        """Shorthand for finding an element by its ``data-testid``."""
        return self.driver.find_element(By.CSS_SELECTOR, f"[data-testid='{testid}']")

    def find_all_by_testid(self, testid: str) -> list[WebElement]:
        """Return all elements matching the given ``data-testid``."""
        return self.driver.find_elements(By.CSS_SELECTOR, f"[data-testid='{testid}']")

    def get_text_stable(
        self, locator: tuple[str, str], timeout: int = DEFAULT_TIMEOUT
    ) -> str:
        """Return text of *locator*, retrying on StaleElementReferenceException."""
        deadline = time.time() + timeout
        while True:
            try:
                el = self.wait_for_element_visible(
                    locator, timeout=min(5, max(1, int(deadline - time.time())))
                )
                return el.text
            except StaleElementReferenceException:
                if time.time() >= deadline:
                    raise
                time.sleep(0.2)

    def get_page_title(self) -> str:
        """Return the text content of the standard page-title element."""
        return self.get_text_stable(PAGE_TITLE)

    def is_error_displayed(self) -> bool:
        """Check whether the standard error element is visible."""
        elements = self.driver.find_elements(*ERROR_DISPLAY)
        return len(elements) > 0 and elements[0].is_displayed()

    # ── Interactions ─────────────────────────────────────────────────────

    def close_dropdown(self, timeout: int = 5) -> None:
        """Close any open select dropdown and wait until it leaves the DOM.

        Guarded per spec/project/e2e-test-stability/ §Hazard-prone UI
        interactions: (1) return immediately when the dropdown is already
        gone, (2) wait briefly for it to close on its own, (3) send ESC only
        while it is verifiably still open, then (4) wait for it to be gone.
        A blind ESC-to-body races the dropdown's self-close and lands in the
        parent dialog instead.

        Tuned for Material-UI's `<Select>` (options rendered as
        ``li[role='option']``); adapt the option locator to your component
        library.
        """
        from selenium.common.exceptions import TimeoutException
        from selenium.webdriver.common.keys import Keys

        option = (By.CSS_SELECTOR, "li[role='option']")
        # (1) Already closed: nothing to dismiss.
        if not self.driver.find_elements(*option):
            return
        # (2) Wait briefly — many selects close themselves after a pick.
        try:
            WebDriverWait(self.driver, 1).until(
                lambda d: len(d.find_elements(*option)) == 0
            )
            return
        except TimeoutException:
            pass
        # (3) Verifiably still open: only now is ESC safe to send.
        if not self.driver.find_elements(*option):
            return
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        # (4) Wait until it is gone.
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(*option)) == 0
            )
        except TimeoutException:
            pass

    def scroll_and_click(self, element: WebElement, attempts: int = 3) -> None:
        """Scroll an element into view and click it with a real click.

        Retries with a fresh scroll correction when the click is intercepted
        by a transient overlay (snackbar, collapse animation) and fails loudly
        once the attempts are exhausted. Deliberately never falls back to a
        scripted ``arguments[0].click()``: an untrusted JS click is forbidden
        by spec/project/e2e-test-stability/ §C (decision-procedure step 5) and
        is a silent no-op on mousedown-only openers such as MUI's ``Select`` —
        the helper would report success while nothing happened.
        """
        last_error: Exception | None = None
        for _ in range(attempts):
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            try:
                element.click()
                return
            except (
                ElementNotInteractableException,
                ElementClickInterceptedException,
            ) as exc:
                last_error = exc
                # Bounded, justified: give a transient overlay (snackbar,
                # collapse animation) time to clear before the next attempt.
                time.sleep(0.3)
        raise ElementClickInterceptedException(
            f"scroll_and_click: real click failed after {attempts} attempts "
            f"({type(last_error).__name__}: {last_error}). Not falling back to "
            "a scripted click per spec/project/e2e-test-stability/ §C — fix "
            "the overlay/geometry or address a different target instead."
        ) from last_error

    def clear_and_fill(
        self, element: WebElement, value: str, timeout: int = 5
    ) -> None:
        """Reliably clear an input, type a new value, and verify it stuck.

        Clears via the native value setter and dispatches input/change events
        so a controlled component (React/Vue) picks up the change, then verifies
        the field is empty and falls back to Ctrl+A before typing if framework
        state restored the old value. After typing, reads the value back with a
        bounded wait and fails loudly when the target value never materializes
        (spec/project/e2e-test-stability/ §D: a state-changing helper verifies
        its effect) — against a readonly or otherwise non-typable field the
        keystrokes are silently dropped, and a helper without the read-back
        would report a successful edit. Adapt if your front end is not
        controlled-component based.
        """
        from selenium.common.exceptions import TimeoutException
        from selenium.webdriver.common.keys import Keys

        self.driver.execute_script(
            "var el = arguments[0];"
            "var proto = el.tagName === 'TEXTAREA'"
            "  ? window.HTMLTextAreaElement.prototype"
            "  : window.HTMLInputElement.prototype;"
            "var setter = Object.getOwnPropertyDescriptor(proto, 'value').set;"
            "setter.call(el, '');"
            "el.dispatchEvent(new Event('input', {bubbles: true}));"
            "el.dispatchEvent(new Event('change', {bubbles: true}));",
            element,
        )
        time.sleep(0.15)  # debounce: bounded, justified (framework event flush)
        current = element.get_attribute("value") or ""
        if current:
            element.send_keys(Keys.CONTROL + "a")
            time.sleep(0.05)
        element.send_keys(value)
        # Read back with bounded retries; fail loudly when the value never
        # arrives instead of letting the test assert against the old state.
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: (element.get_attribute("value") or "") == value
            )
        except TimeoutException as exc:
            actual = element.get_attribute("value") or ""
            raise AssertionError(
                f"clear_and_fill: field value never became {value!r} within "
                f"{timeout}s; last read-back was {actual!r} (readonly or "
                "non-typable field?)"
            ) from exc

    def navigate_via_sidebar(self, path: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Navigate by clicking a sidebar link, simulating real user behaviour.

        Falls back to direct URL navigation when the sidebar item is not
        visible. Assumes nav links carry ``data-testid='nav-<path>'``.
        """
        locator = (By.CSS_SELECTOR, f"[data-testid='nav-{path}']")
        items = self.driver.find_elements(*locator)
        if items and items[0].is_displayed():
            self.scroll_and_click(items[0])
            WebDriverWait(self.driver, timeout).until(EC.url_contains(path))
        else:
            self.navigate(path)

    # ── Screenshots ───────────────────────────────────────────────────────

    def take_screenshot(self, name: str, output_dir: Path) -> Path:
        """Save a PNG screenshot and return the file path."""
        filepath = output_dir / f"{name}.png"
        self.driver.save_screenshot(str(filepath))
        return filepath
