"""The BDD-independent page object for the reference profile of
spec/project/bdd-page-object-integration/.

Illustrative and non-normative. This is the load-bearing file for the spec's
thesis, so read its imports first: **Selenium only.** There is no `pytest_bdd`
import, no `@given`/`@when`/`@then` decorator, no assertion, and no knowledge of
scenarios, tags, or the test runner. It exposes named methods and returns page
state; the caller (a BDD step *or* a plain test) decides what to assert.

Because it depends on nothing above it, the same object is reused unchanged by
`steps/test_watering_bdd.py` and by `test_watering_plain.py`.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By

from .base_page import BasePage


class WateringDashboardPage(BasePage):
    """Encapsulates the watering-dashboard screen. Selectors live here only,
    resolved against the data-testid contract of testability-identifiers."""

    def _row(self, name: str) -> tuple[str, str]:
        return (By.CSS_SELECTOR, f'[data-testid="plant-row-{name}"]')

    def open(self) -> "WateringDashboardPage":
        self._open("/watering")
        self._visible((By.CSS_SELECTOR, '[data-testid="watering-dashboard"]'))
        return self

    def is_due(self, name: str) -> bool:
        row = self._visible(self._row(name))
        return row.get_attribute("data-due") == "true"

    def record_watering(self, name: str) -> None:
        self._visible(
            (By.CSS_SELECTOR, f'[data-testid="water-{name}"]')
        ).click()

    def next_reminder_days(self, name: str) -> int:
        row = self._visible(self._row(name))
        return int(row.get_attribute("data-next-reminder-days"))
