"""Illustrative, non-normative step definitions for the BDD reference profile of
spec/project/behavior-driven-development/.

This is the ``pytest-bdd`` flavour, chosen to compose with the Selenium + pytest
reference profile of spec/project/e2e-test-automation/. A project on another BDD
stack satisfies the spec's binding core without this file.

What it demonstrates from the spec's *Step-definition design* group:

* Each step is **thin**: it translates one Gherkin line into a call on the
  page-object layer and holds no business logic of its own.
* Steps are **reused** across scenarios (the same ``Given`` serves several).
* No assertion lives in the ``.feature`` file; the ``Then`` *binding* asserts,
  while the scenario text states the expected outcome in domain terms.
* No selector, wait, or click appears here: the page object owns selector
  resolution (spec/frontend/testability-identifiers/) and the execution mechanics
  (spec/project/e2e-test-automation/).
"""

from __future__ import annotations

from pytest_bdd import given, parsers, scenarios, then, when

# Bind every scenario in the feature file. The @TC-… tags travel with them, so a
# runner can select or report by test-case ID (traceability, per the spec).
scenarios("../features/plant_watering.feature")


# --- Background steps (reused by every scenario) ---------------------------------


@given("I am signed in as a plant owner")
def sign_in(dashboard_page):
    # Thin: delegates to the page object; no selectors, no waits here.
    dashboard_page.sign_in_as_plant_owner()


@given(parsers.parse('I own a plant "{name}" with a watering interval of {days:d} days'))
def own_plant(dashboard_page, name, days):
    dashboard_page.create_plant(name=name, interval_days=days)


# --- Given: preconditions --------------------------------------------------------


@given(parsers.parse('"{name}" was last watered {days:d} days ago'))
def last_watered(dashboard_page, name, days):
    dashboard_page.set_last_watered_days_ago(name=name, days=days)


@given(parsers.parse('"{name}" is due for watering'))
def make_due(dashboard_page, name):
    # Reuses the same domain operation; keeps the precondition declarative.
    dashboard_page.set_last_watered_days_ago(name=name, days=7)


# --- When: the triggering event --------------------------------------------------


@when("I open my watering dashboard")
def open_dashboard(dashboard_page):
    dashboard_page.open()


@when(parsers.parse('I record that I watered "{name}"'))
def record_watering(dashboard_page, name):
    dashboard_page.record_watering(name=name)


# --- Then: the expected observable outcome (the binding asserts) ------------------


@then(parsers.parse('"{name}" is shown as due for watering'))
def assert_due(dashboard_page, name):
    assert dashboard_page.is_due(name) is True


@then(parsers.parse('"{name}" is not shown as due for watering'))
def assert_not_due(dashboard_page, name):
    assert dashboard_page.is_due(name) is False


@then(parsers.parse('"{name}" is shown as "{status}" for watering'))
def assert_status(dashboard_page, name, status):
    expected_due = status == "due"
    assert dashboard_page.is_due(name) is expected_due


@then(parsers.parse("the next reminder is scheduled {days:d} days ahead"))
def assert_next_reminder(dashboard_page, days):
    assert dashboard_page.days_until_next_reminder() == days
