# BDD ↔ Page Object integration reference profile (illustrative, non-normative)

This directory makes the tool-neutral core of
`spec/project/bdd-page-object-integration/` concrete with one worked example in
the **Selenium + `pytest-bdd`** reference profile. It is illustrative: a project
on another stack (Playwright/Cypress; Cucumber-JVM/Cucumber.js) satisfies the
binding core without it.

The whole point of the example is to **prove the decoupling**: one page object,
driven unchanged from both a BDD step and a plain (non-BDD) test.

## Files

- `pages/base_page.py` — a minimal page-object base (driver + navigation/wait
  helpers). In a real project this base is owned by
  `spec/project/e2e-test-automation/`; it is inlined here only so the example
  stands alone.
- `pages/watering_dashboard_page.py` — **the BDD-independent page object.** Note
  what it imports: only Selenium. It carries no `pytest_bdd` import, no
  `@given`/`@when`/`@then`, no assertions, and no knowledge of scenarios or tags.
  It exposes named methods and returns page state.
- `features/watering.feature` — a small Gherkin feature.
- `steps/test_watering_bdd.py` — the **step-as-glue** layer: a `pytest-bdd`
  module that injects the driver and the page object via fixtures, holds a
  scenario-scoped `context` fixture for shared state, and asserts in the `Then`
  binding. This is the only file that imports both `pytest_bdd` and the page
  object.
- `test_watering_plain.py` — a **plain `pytest` E2E test** that imports and drives
  the *same* `WateringDashboardPage` unchanged, with no `pytest_bdd` anywhere.
  This is the reuse proof the spec requires.

## What this demonstrates from the spec

- **Dependency direction / independence:** the page object imports only Selenium;
  the dependency is one-way (steps → page object), so the page object is reusable.
- **Step-as-glue:** the step file is the only layer aware of both worlds; it holds
  no selectors/waits and asserts only in the `Then` binding.
- **Wiring:** dependency injection via `pytest` fixtures; one driver provider;
  scenario state in a scenario-scoped `context`, never on the page object.
- **Reuse beyond BDD:** `test_watering_plain.py` drives the same page object, so
  the decoupling is demonstrable, not asserted.
