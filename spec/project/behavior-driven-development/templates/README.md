# BDD reference profile (illustrative, non-normative)

This directory makes the tool-neutral core of
`spec/project/behavior-driven-development/` concrete with one worked example in
the **Gherkin + Cucumber family** reference profile. It's illustrative: a project
on another BDD stack satisfies the spec's binding core without adopting any of
these files.

The `pytest-bdd` flavour is chosen to match the Python reference profile of
`spec/project/e2e-test-automation/`, so the two profiles compose: the step
definitions here delegate down into that spec's page-object layer.

## Files

- `features/plant_watering.feature` — a worked Gherkin feature file showing:
  - an intention-revealing `Feature:` and `Scenario:` titles that name behavior,
  - a `Background:` for the precondition shared by every scenario (setup only,
    no `When`/`Then`),
  - a declarative `Scenario:` (behavior in domain terms, no selectors or clicks),
  - a `Scenario Outline:` with an `Examples:` table for a boundary-value data set,
  - `@TC-…` tags binding each scenario to its source test-case ID for traceability.
- `steps/test_plant_watering_steps.py` — a thin `pytest-bdd` step-definition
  skeleton: each step translates one Gherkin line into a call on the page-object
  layer and holds no business logic; the `Then` binding performs the assertion
  while the scenario text stays declarative.

## What this demonstrates from the spec

- The derivation workflow: one scenario per TC behavior, precondition → `Given`,
  action → `When`, expected result → `Then`, and a `@TC-…` tag for machine-checkable
  traceability.
- Step-definition design: thin steps, cross-scenario reuse, no assertions in the
  `.feature` file, selectors resolved only through the page-object layer.
- BDD on E2E: the scenario layer sits above `e2e-test-automation`'s execution
  machinery, which owns waits, screenshots, and selector resolution.
