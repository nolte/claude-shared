"""The step-as-glue layer for the reference profile of
spec/project/bdd-page-object-integration/.

Illustrative and non-normative. This is the ONLY file that imports both worlds:
`pytest_bdd` (the BDD framework) and the page object. It demonstrates the wiring
contract:

* Dependency injection: `pytest` fixtures build the driver and the page object
  and inject them; the step body never constructs driver plumbing.
* A single driver provider (`driver` fixture) shared into the page object.
* Scenario state lives in a scenario-scoped `context` fixture, never on the page
  object and never in a module global.
* Steps hold no selectors, no waits, no business logic; the `Then` binding is
  where the assertion lives.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from selenium import webdriver

from ..pages.watering_dashboard_page import WateringDashboardPage

scenarios("../features/watering.feature")


# --- wiring: dependency injection via fixtures ----------------------------------


@pytest.fixture
def driver():
    drv = webdriver.Chrome()
    yield drv
    drv.quit()


@pytest.fixture
def dashboard(driver) -> WateringDashboardPage:
    # The step layer wires the page object; the page object knows nothing of this.
    return WateringDashboardPage(driver)


@pytest.fixture
def context() -> dict:
    # Scenario-scoped shared state — NOT stored on the page object.
    return {}


# --- steps: thin glue, assertions only in the Then binding ----------------------


@given("the watering dashboard is open")
def open_dashboard(dashboard: WateringDashboardPage) -> None:
    dashboard.open()


@when(parsers.parse('I record that I watered "{name}"'))
def record_watering(dashboard: WateringDashboardPage, context: dict, name: str) -> None:
    context["name"] = name
    dashboard.record_watering(name)


@then(parsers.parse('"{name}" is shown as due for watering'))
def assert_due(dashboard: WateringDashboardPage, name: str) -> None:
    assert dashboard.is_due(name) is True


@then(parsers.parse('the next reminder for "{name}" is {days:d} days away'))
def assert_next_reminder(dashboard: WateringDashboardPage, name: str, days: int) -> None:
    assert dashboard.next_reminder_days(name) == days
