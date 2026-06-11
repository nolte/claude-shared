"""Example page object for a list/CRUD page.

A worked example of the page-object pattern the spec requires: locators grouped
and data-testid-first, an ``open()`` that waits for page content, page state and
interactions exposed as named methods. Copy this shape for your real pages and
replace the ``/items`` route and the ``item-*`` test hooks with your app's.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from .base_page import BasePage


class ExampleListPage(BasePage):
    """Interact with a list page (``/items``)."""

    PATH = "/items"

    # ── Page markers ──
    PAGE = (By.CSS_SELECTOR, "[data-testid='items-page']")
    # ── Locators (grouped by function) ──
    ROW = (By.CSS_SELECTOR, "[data-testid^='item-row-']")
    CREATE_BUTTON = (By.CSS_SELECTOR, "[data-testid='item-create-button']")
    NAME_INPUT = (By.CSS_SELECTOR, "[data-testid='item-form-name'] input")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "[data-testid='item-form-submit']")

    def __init__(self, driver: WebDriver, base_url: str) -> None:
        super().__init__(driver, base_url)

    def open(self) -> "ExampleListPage":
        """Navigate to the page and wait for its content to load."""
        self.navigate(self.PATH)
        self.wait_for_element(self.PAGE)
        self.wait_for_loading_complete()
        return self

    # ── Page state ──
    def get_row_count(self) -> int:
        return len(self.driver.find_elements(*self.ROW))

    # ── Interactions ──
    def click_create(self) -> None:
        self.wait_for_element_clickable(self.CREATE_BUTTON).click()

    def fill_name(self, value: str) -> None:
        self.clear_and_fill(self.wait_for_element_visible(self.NAME_INPUT), value)

    def submit(self) -> None:
        self.wait_for_element_clickable(self.SUBMIT_BUTTON).click()
        self.wait_for_loading_complete()
