# BDD and Page Object Integration

Status: draft
Portfolio-Scope: portfolio

## Context

At the end-to-end tier a BDD scenario and a Page Object both exist, and the value of the pairing depends entirely on *how they are wired together*. Done well, a Gherkin scenario reads as behavior in the domain's language, a thin step definition translates each line into a call on a page object, and the page object encapsulates the user interface, so the same page object serves every scenario that touches that screen. Done badly, the page object learns about Gherkin, the step definition reaches into the DOM, assertions leak across layers, and every scenario grows its own bespoke page object that no other test can reuse. The difference isn't the two patterns in isolation, both of which are already specified elsewhere: it's the **integration contract** between them, and specifically the **decoupling** that keeps the page-object layer reusable.

This spec owns that contract. Its load-bearing thesis is a strict dependency direction: **the Page Object layer MUST have zero dependency on the BDD/step layer.** A page object knows nothing of Gherkin, of the step-definition framework, of scenarios, tags, or the test runner, and it holds no assertions. It's a plain, reusable user-interface encapsulation library that a BDD step definition consumes exactly the way a non-BDD test consumes it. The step definition is the *only* layer that knows both worlds; it depends on page objects, page objects never depend on it. That one-way dependency is what makes a page object reusable across BDD steps, plain E2E tests, and any other client, which is the whole point of investing in the pattern.

The normative core is tool-neutral: it constrains the *dependency direction, the decoupling, and the wiring seam* against any WebDriver-plus-BDD combination. Because the operator's primary case is Selenium, a normative **Selenium + `pytest-bdd`** reference profile makes the contract concrete, mirroring how `spec/project/e2e-test-automation/` demotes its concrete stack to a swappable profile.

**Relationship to the other specs.** Bounded by responsibility:

- `spec/project/e2e-test-automation/` [R1] owns the Page Object Model *itself*: encapsulation, the shared base, named methods, deterministic waiting, locator strategy, and where assertions live. This spec **MUST NOT** restate those internals; it references them and adds the integration/decoupling layer on top.
- `spec/project/behavior-driven-development/` [R2] owns the step-definition *principles* (thin steps that delegate, no assertions in Gherkin) and the scenario language. This spec references those and specifies the concrete wiring and the dependency direction the two layers meet on.
- `spec/frontend/testability-identifiers/` [R3] owns the stable selector contract a page object resolves against. This spec never names a selector.
- `spec/project/test-pyramid-foundation/` [R4] owns the tier model; this spec governs the E2E-tier integration only.

Readers: engineers who wire BDD scenarios to page objects or review that wiring; agent/skill authors building a BDD-scenario or page-object capability; reviewers checking that a page object stayed reusable and free of BDD coupling.

## Goals

- State the BDD-to-Page-Object integration contract once, tool-neutrally, as the binding core every consuming project satisfies
- Make the **one-way dependency** (steps depend on page objects, never the reverse) the load-bearing rule, so the page-object layer stays reusable
- Keep the page-object layer usable unchanged from a non-BDD test, proving the decoupling rather than asserting it
- Specify the wiring seam concretely: how page objects reach the step layer, where scenario state lives, and where assertions sit
- Ship one normative Selenium + `pytest-bdd` reference profile that demonstrates the decoupling with runnable code
- Name the coupling anti-patterns so a reviewer can reject them
- Reference the page-object and step-definition owners instead of restating them

## Non-Goals

- Specifying the Page Object Model's own internals (encapsulation, shared base, named methods, deterministic waiting, locator strategy, where assertions live): owned by `spec/project/e2e-test-automation/` [R1]; this spec consumes that discipline and governs only the integration with BDD
- Specifying the scenario language or the general step-definition principles (thin steps, no assertions in Gherkin, declarative scenarios): owned by `spec/project/behavior-driven-development/` [R2]
- Provisioning the stable selectors a page object resolves against: owned by `spec/frontend/testability-identifiers/` [R3]
- Deriving test cases or scenarios from requirements: owned by `spec/project/test-case-derivation/` and `spec/project/behavior-driven-development/` [R2]
- Mandating a specific browser-automation library or BDD framework: the core is tool-neutral; Selenium and `pytest-bdd` are the illustrative reference profile
- Setting the tier taxonomy or coverage governance: owned by `spec/project/test-pyramid-foundation/` [R4]

## Requirements

### Dependency direction and layering

- The stack **MUST** be layered in exactly this order, each layer depending only on the one below it: Gherkin scenario → step definition → page object → browser-automation driver. Dependencies **MUST** point downward only.
- The dependency between the step layer and the page-object layer **MUST** be one-way: a step definition depends on page objects; a page object **MUST NOT** depend on, import, or reference any step definition, step-framework symbol, or Gherkin construct.
- Each layer **MUST** have a single responsibility: the scenario states behavior, the step definition translates and orchestrates, the page object encapsulates the user interface, the driver performs the raw automation. A responsibility **MUST NOT** migrate up or down a layer (no UI plumbing in a step, no behavior wording in a page object).

### Page-object independence from BDD (the reuse contract)

- A page object **MUST** be free of every BDD and test-framework coupling: it **MUST NOT** import or reference the BDD framework (for example `pytest_bdd` / Cucumber symbols), **MUST NOT** carry step decorators (`@given` / `@when` / `@then`), and **MUST NOT** know about scenarios, tags, feature files, or the test runner.
- A page object **MUST NOT** contain test assertions; it exposes page state through named methods and returns it, and the assertion is made by the caller (per `spec/project/e2e-test-automation/` [R1]). An assertion inside a page object couples it to a test's expectations and destroys its reuse.
- A page object **MUST** be usable, unchanged, by a client other than the BDD step (a plain E2E test, a smoke check, a script). This reusability **MUST** be demonstrable, not assumed: a project **SHOULD** exercise at least one page object from both a BDD step and a non-BDD test to prove the decoupling holds.
- The page-object layer as a whole **MUST** form a standalone, reusable user-interface encapsulation library, independent of the reason any particular client drives it.

### The step-as-glue contract

- The step definition **MUST** be the only layer aware of both worlds: it binds one Gherkin step and translates it into one or a few calls on page objects. It **MUST** hold no user-interface plumbing (no raw driver calls, no selectors, no waits, no screenshots) and no business logic of its own.
- A step definition **MUST NOT** reach past the page-object layer into the driver or the DOM; every user-interface interaction **MUST** go through a page object.
- The assertion for a `Then` step **MUST** live in that step's binding, comparing state returned by a page object against the scenario's expected outcome; the assertion **MUST NOT** live in the page object and **MUST NOT** live in the Gherkin text.
- A step definition **SHOULD** stay declarative in what it expresses, so that reading the step bindings alongside the feature file still communicates behavior rather than automation mechanics.

### Wiring and dependency provision

- Page objects **MUST** be provided to step definitions by **dependency injection**, not constructed with inline driver plumbing inside the step body: the reference mechanisms are test fixtures (`pytest` fixtures for `pytest-bdd`) or a DI container (for example PicoContainer for Cucumber-JVM). A step receives a ready page object; it doesn't wire up the driver itself.
- The browser-automation session/driver **MUST** be owned by a single provider (a fixture or container binding) and shared into page objects through that provider, so one scenario drives one session and page objects never instantiate their own driver.
- Page-object construction **MUST NOT** duplicate per step: a page object is defined once and injected wherever needed; a project **MUST NOT** re-instantiate bespoke page-object plumbing in each step.

### State and data at the seam

- State shared across the steps of a scenario (the entity under test, an id captured in a `When`, a value to assert in a `Then`) **MUST** be held in an explicit **scenario-scoped context** object (a `pytest-bdd` fixture, a Cucumber World), never in module-level global variables or class attributes on a page object.
- A page object **MUST NOT** persist scenario-specific state across scenarios; it exposes current page state on demand and stays stateless with respect to the test flow.
- Data a step passes to a page object (a name, an amount, a row from an `Examples` table) **MUST** flow as method arguments; a page object **MUST NOT** read the scenario context, tags, or example data directly, which would couple it back to BDD.

### Composition

- A single step **MAY** orchestrate several page objects (open one page, act, assert on another); the orchestration lives in the step, not spread across the page objects.
- A page object **MAY** return another page object to model navigation (a method that navigates returns the destination page's object); such composition **MUST** stay within the page-object layer and **MUST NOT** reference any step or scenario.
- A project **MUST NOT** create a page object per step or per scenario; page objects are keyed to user-interface surfaces (a page, a component, a dialog), and reuse across steps is the expected outcome. One-page-object-per-step is a coupling smell that defeats the reuse contract.

### Reuse beyond BDD

- The same page object **MUST** drive both a BDD step and a non-BDD test with no change to the page object. Where a project ships the reference profile, it **MUST** include an example demonstrating this dual use (see the reference profile and `templates/`).
- Cross-cutting page-object concerns (navigation, waiting, base helpers) **MUST** live in the page-object base owned by `spec/project/e2e-test-automation/` [R1], so every client, BDD or not, inherits the same behavior; this spec **MUST NOT** restate that base's contents.

### Anti-patterns

- The following **MUST** be treated as defects and rejected in review:
  - **A page object that imports the BDD framework** or carries `@given` / `@when` / `@then` decorators: the layers are fused and reuse is gone.
  - **Assertions inside a page object**: it now encodes a test's expectations and can't be reused by a client with different expectations.
  - **A step that calls the driver or a selector directly**, bypassing the page object: the step absorbed page-object responsibility.
  - **Business logic in a page object**: behavior leaked down out of the step/scenario.
  - **A page object aware of scenarios, tags, or the scenario context**: an upward dependency that inverts the layering.
  - **One page object per step or per scenario**: bespoke, single-use objects that defeat the pattern's purpose.
  - **Scenario state shared through global variables or on the page object** instead of an explicit scenario-scoped context.
  - **A god page object** that spans unrelated surfaces, so no client can reuse a focused slice.

## Reference profile (illustrative, non-normative)

This profile makes the tool-neutral core concrete with **Selenium** and **`pytest-bdd`**, composing with the Selenium + pytest reference profile of `spec/project/e2e-test-automation/` [R1] and the `pytest-bdd` profile of `spec/project/behavior-driven-development/` [R2]. A project on another stack (Playwright, Cypress; Cucumber-JVM, Cucumber.js) satisfies the core without it. The shipped `templates/` directory carries a worked example.

- **Page objects** are plain classes that receive a Selenium `WebDriver` (or a wrapper) through their constructor, expose named methods, and import nothing from `pytest_bdd`. They resolve `spec/frontend/testability-identifiers/` [R3] selectors through the base owned by `spec/project/e2e-test-automation/` [R1].
- **Step definitions** live in a `pytest-bdd` module; a `pytest` fixture builds the driver and each page object and injects them, plus a scenario-scoped `context` fixture holds shared state. Each step calls page-object methods; each `Then` step asserts on returned state.
- The shipped `templates/` carries: a BDD-independent page object (`pages/`), a `pytest-bdd` step file that wires to it, and a **plain `pytest` E2E test that drives the same page object unchanged**, proving the decoupling.

## Acceptance Criteria

- [ ] The one-way dependency (steps → page objects, never the reverse) is stated as the load-bearing MUST
- [ ] Page-object independence from BDD is specified: no BDD/framework imports, no step decorators, no scenario/tag/runner awareness, no assertions
- [ ] The step-as-glue contract is specified: only layer aware of both worlds, no UI plumbing, no business logic, `Then` assertion in the step binding
- [ ] Wiring is specified: dependency injection via fixtures/DI container, a single driver provider, no per-step page-object plumbing
- [ ] Scenario state is specified to live in an explicit scenario-scoped context, never global variables or the page object
- [ ] Composition and reuse-beyond-BDD are specified, including the demonstrable dual-use (BDD step + non-BDD test) of the same page object
- [ ] The Non-Goals link all four neighbour specs (`e2e-test-automation`, `behavior-driven-development`, `testability-identifiers`, `test-pyramid-foundation`) by responsibility, restating none of them
- [ ] The anti-pattern list names framework imports in a page object, assertions in a page object, driver/selector calls in a step, business logic in a page object, scenario awareness in a page object, one-object-per-step, global state, and god page objects
- [ ] A Selenium + `pytest-bdd` reference profile ships with a `templates/` example proving the decoupling (same page object from a BDD step and a plain test)
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/e2e-test-automation/`: owns the Page Object Model internals (encapsulation, base, named methods, waits, locators, assertions-in-tests) this spec consumes
- [R2] `spec/project/behavior-driven-development/`: owns the step-definition principles and scenario language this spec wires to page objects
- [R3] `spec/frontend/testability-identifiers/`: owns the stable selector contract a page object resolves against
- [R4] `spec/project/test-pyramid-foundation/`: owns the tier model; this spec governs the E2E-tier integration only
- [R5] Martin Fowler, *PageObject* (the page-object encapsulation pattern): <https://martinfowler.com/bliki/PageObject.html>
- [R6] Selenium, *Page object models* (page objects as a reusable UI abstraction): <https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/>
- [R7] `pytest-bdd` documentation (steps as fixtures; dependency injection): <https://pytest-bdd.readthedocs.io/>
- [R8] Cucumber, *Dependency Injection* (World / container-provided state and page objects): <https://cucumber.io/docs/cucumber/state/>

## Open Questions

- Should the reference profile ship a second wiring flavor (Cucumber-JVM + PicoContainer) alongside `pytest-bdd`, or does one worked example keep the profile illustrative?
- Should the demonstrable dual-use of a page object (from a BDD step and a non-BDD test) be a hard review gate, or a strong SHOULD?
- Where a project has no non-BDD E2E tests at all, is the reuse contract still verifiable by a dedicated reuse example, or does it relax to a design-review check?
