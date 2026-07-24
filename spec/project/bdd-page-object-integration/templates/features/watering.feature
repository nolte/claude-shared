# Illustrative, non-normative. Feature for the reference profile of
# spec/project/bdd-page-object-integration/. The scenarios stay declarative; the
# selectors and waits live in the page object, not here.

Feature: Watering dashboard

  @TC-051
  Scenario: A due plant is shown as due
    Given the watering dashboard is open
    Then "Monstera" is shown as due for watering

  @TC-052
  Scenario: Watering a plant clears its reminder
    Given the watering dashboard is open
    When I record that I watered "Monstera"
    Then the next reminder for "Monstera" is 7 days away
