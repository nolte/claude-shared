"""The reuse proof for the reference profile of
spec/project/bdd-page-object-integration/.

Illustrative and non-normative. This is a plain `pytest` end-to-end test with NO
`pytest_bdd` anywhere. It imports and drives the *same* `WateringDashboardPage`
that `steps/test_watering_bdd.py` uses, unchanged. Because the page object has no
dependency on the BDD layer, both clients reuse it as-is — which is exactly the
decoupling the spec requires to be demonstrable rather than assumed.
"""

from __future__ import annotations

import pytest
from selenium import webdriver

from .pages.watering_dashboard_page import WateringDashboardPage


@pytest.fixture
def dashboard():
    driver = webdriver.Chrome()
    try:
        yield WateringDashboardPage(driver)
    finally:
        driver.quit()


def test_due_plant_is_flagged(dashboard: WateringDashboardPage) -> None:
    dashboard.open()
    assert dashboard.is_due("Monstera") is True


def test_watering_resets_the_reminder(dashboard: WateringDashboardPage) -> None:
    dashboard.open()
    dashboard.record_watering("Monstera")
    assert dashboard.next_reminder_days("Monstera") == 7
