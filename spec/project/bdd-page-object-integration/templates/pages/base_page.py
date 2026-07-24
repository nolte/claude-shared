"""Minimal page-object base for the BDD ↔ Page Object integration reference
profile of spec/project/bdd-page-object-integration/.

Illustrative and non-normative. In a real project this base is owned by
spec/project/e2e-test-automation/ (navigation, waiting, interaction helpers); it
is inlined here only so the example stands alone. Note the imports: Selenium
only. Nothing from pytest_bdd, no assertions, no test-runner awareness.
"""

from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Common navigation and condition-based waiting for every page object."""

    base_url = "http://localhost:5173"

    def __init__(self, driver: WebDriver, timeout: float = 10.0) -> None:
        self._driver = driver
        self._wait = WebDriverWait(driver, timeout)

    def _open(self, path: str) -> None:
        self._driver.get(f"{self.base_url}{path}")

    def _visible(self, locator: tuple[str, str]) -> WebElement:
        # Condition-based wait, never a sleep (see e2e-test-automation).
        return self._wait.until(EC.visibility_of_element_located(locator))
