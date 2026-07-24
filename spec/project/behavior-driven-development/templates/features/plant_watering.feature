# Illustrative, non-normative. Reference profile for
# spec/project/behavior-driven-development/. A project on another BDD stack
# satisfies the spec's binding core without this file.
#
# Note how the scenarios stay declarative: they name the behavior in the domain's
# ubiquitous language and never mention a selector, a click, or a wait. Those
# live in the step layer, which delegates to e2e-test-automation's page objects.

Feature: Watering reminders for houseplants
  As a plant owner
  I want to be reminded when a plant is due for watering
  So that no plant is forgotten or overwatered.

  Background:
    Given I am signed in as a plant owner
    And I own a plant "Monstera" with a watering interval of 7 days

  @TC-041
  Scenario: A plant becomes due on its watering day
    Given "Monstera" was last watered 7 days ago
    When I open my watering dashboard
    Then "Monstera" is shown as due for watering

  @TC-042
  Scenario: A recently watered plant is not yet due
    Given "Monstera" was last watered 2 days ago
    When I open my watering dashboard
    Then "Monstera" is not shown as due for watering

  @TC-043
  Scenario: Watering a due plant clears the reminder
    Given "Monstera" is due for watering
    When I record that I watered "Monstera"
    Then "Monstera" is not shown as due for watering
    And the next reminder is scheduled 7 days ahead

  # One behavior exercised across a boundary-value data set: the due/not-due edge
  # around the interval. One row per source test case, one scenario, no copy-paste.
  @TC-044
  Scenario Outline: Due status around the watering interval boundary
    Given "Monstera" was last watered <days> days ago
    When I open my watering dashboard
    Then "Monstera" is shown as "<status>" for watering

    Examples:
      | days | status  |
      | 6    | not due |
      | 7    | due     |
      | 8    | due     |
