# End-to-End Test Automation Standard

Status: draft

## Context

An end-to-end (E2E) test drives the real user-facing surface of a running system and asserts on what the user can observe. The valuable, reusable part of E2E work isn't the test code itself but the **discipline** that keeps a suite trustworthy: every interaction goes through a page object so selectors live in one place, every wait is a condition rather than a sleep so the suite isn't flaky, every test leaves a screenshot trail and a machine-generated protocol so a run is auditable, every test traces back to the requirement it verifies, and the suite as a whole covers all the test tiers rather than piling everything into slow browser tests. That discipline is framework-independent. The throwaway part is the stack glue: which library drives the browser, which directory holds the suite, which domain selectors and routes a given app exposes.

This spec governs that reusable discipline. It's the generalised core of a project-local E2E toolchain (kamerplanter's `NFR-008` test strategy and `NFR-008a` Selenium standard) that hard-coded one app's Python/Selenium/pytest stack, its German requirement-ID scheme (`REQ-NNN`), its routes (`/pflanzen/…`), and its `http://localhost:5173` dev server. The portfolio form states the discipline framework-neutrally as the binding core, then pins one concrete, fully worked **reference profile** (Selenium + pytest) as a normative appendix so a Python project gets a batteries-included default while other stacks (Playwright, Cypress) implement the same core.

It's operationalised by three agents and one skill:

- `e2e-test-generator` (`distribution: plugin`)—scaffolds a spec-conformant E2E suite for a feature
- `e2e-test-reviewer` (`distribution: plugin`)—reviews and minimally repairs an existing suite against this spec
- `e2e-result-reviewer` (`distribution: plugin`)—visually reviews a run's screenshots and protocol against the requirement specs
- `test-pyramid-check` (skill)—audits a feature's test-tier completeness against the tier taxonomy in `spec/project/test-pyramid-foundation/` and the E2E discipline in this spec

**Relationship to `test-case-derivation`.** That spec deliberately scoped E2E-automation code generation/review, test-tier auditing, and screenshot review *out* of the plugin, on the grounds that they're "too stack-coupled" and "stay project-local." This spec revises that position. The only cited reason was stack coupling, and a framework-neutral binding core with the concrete library demoted to a reference profile resolves exactly that: the discipline is portfolio-reusable, only the profile is stack-specific. `test-case-derivation` is updated in lockstep so the two specs don't contradict each other; the boundary between them is now drawn by responsibility (derive abstract cases vs. automate, run-review, and audit them), not by "shared vs. project-local."

Readers: agent/skill authors maintaining this toolchain; QA engineers and developers who scaffold, review, or audit E2E suites; reviewers verifying that a suite is non-flaky, traceable, and tier-complete.

## Goals

- State the trustworthy-E2E discipline once, framework-neutrally, as the binding core every consuming project's suite must satisfy
- Keep the core executable on any browser-automation stack by demoting the concrete library to a swappable reference profile rather than a requirement
- Ship one fully worked, normative **Selenium + pytest** reference profile so a Python project is productive immediately
- Make every E2E suite auditable (screenshot checkpoints + machine-generated protocol) and traceable (each test names the requirement it verifies)
- Keep the E2E tier reserved for user-journey verification, deferring the full tier model and taxonomy to `spec/project/test-pyramid-foundation/`
- Adapt to the project's stack, paths, routes, and language instead of assuming one app

## Non-Goals

- Deriving abstract, framework-agnostic **test cases** from a requirement document—owned by `spec/project/test-case-derivation/` and its `test-case-extractor` agent; this spec consumes such cases (via their TC-IDs) but doesn't produce them
- Running the unit/lint/typecheck gate and classifying its failures—owned by `spec/project/quality-gate/`; this spec covers the E2E tier's *shape and discipline*, not the gate that executes the fast tiers in CI
- Mandating a specific browser-automation library: the core is framework-neutral; Selenium is the shipped reference profile, not a requirement
- Authoring or editing the requirement/spec documents a suite traces to
- Generating production application code or `data-testid` hooks in the application under test (the suite *relies on* such hooks; adding them is application work). Provisioning those hooks is the provider-side complement, owned by `spec/frontend/testability-identifiers/`
- Authoring the business-readable **BDD scenario/specification layer** (Given-When-Then, feature files) that sits above these execution mechanics—owned by `spec/project/behavior-driven-development/` [R7]; a BDD scenario's steps delegate down into the page objects this spec owns, they don't restate them

## Requirements

### Framework neutrality

- The binding requirements in this section **MUST** be expressed against capabilities every browser-automation stack provides (navigate, locate, wait-for-condition, act, capture screenshot), and **MUST NOT** name a concrete library, language, or runner
- A consuming project **MUST** declare which stack realises the core; absent a declaration, consumers and the consuming agents **MUST** assume the Selenium + pytest reference profile below
- Every concrete artefact this spec ships (directory layout, fixtures, protocol generator, example tests) is part of the **reference profile** and **MAY** be replaced wholesale by a project on a different stack, provided the binding core still holds

### Test-tier completeness (the pyramid)

- The full tier model and the closed functional-tier taxonomy are owned by `spec/project/test-pyramid-foundation/`; this spec **MUST NOT** restate them. A feature's suite **MUST** be tier-complete per that foundation—each behaviour tested at the lowest tier that gives confidence—while this spec governs only the **E2E tier's** shape and discipline
- The **E2E tier MUST** be reserved for user-journey verification, not for logic better tested a tier down; this is the foundation's lowest-tier-that-gives-confidence rule applied at the apex
- The characteristic failure mode is an **over-populated apex**: single-surface, field-level assertions (a field shown/hidden, a button enabled/disabled, an empty state, a label, an i18n string, a validation message, a calculation result) run as slow browser tests instead of fast component/unit tests. A suite drifting into the hundreds of E2E tests is a symptom of this; each such test **MUST** be pushed down to the lowest tier that gives confidence, leaving E2E a lean set of cross-layer journeys
- Coverage governance (coverage as a guide not a target, mutation score as the stronger signal, no fixed cross-tier ratios) is owned by the foundation; this spec **MUST NOT** set numeric coverage targets
- The `test-pyramid-check` skill **MUST** audit tier completeness against the foundation's taxonomy and the E2E discipline defined below, and report, per feature, which tiers are present, which are missing, and whether the E2E tier follows those disciplines

### Page-object encapsulation

- Every UI interaction in a test **MUST** go through a page object; tests **MUST NOT** call the driver's element-lookup primitives directly—raw locator calls live only inside page objects
- Page objects **MUST** share a common base providing the navigation, waiting, and interaction helpers, so a test reads as intent (open, act, assert) and never as raw automation plumbing
- A page object **MUST** expose page state and interactions as named methods; tests assert on returned state, they don't reach into the DOM

### Deterministic waiting

- Tests **MUST NOT** use fixed-duration sleeps to synchronise with the UI; every wait **MUST** be expressed as an explicit condition (presence, visibility, clickability, URL change, loading-indicator gone)
- A fixed sleep **MAY** appear only inside a page object, only for a genuinely time-based concern (a bounded animation or debounce), and **MUST** carry a comment justifying it and a small bound
- A **global implicit wait MUST NOT** be relied on as a synchronisation mechanism. It couples every element lookup to a hidden fixed timeout, composes non-deterministically with explicit condition waits (mixing the two is itself an anti-pattern), and, most costly, makes every *negative* lookup (an intentionally-absent element, a locator-fallback miss) block for the full timeout. Set the implicit wait to zero (or a small floor) and express every wait explicitly; a large implicit wait is the single most common hidden cause of a slow suite

### Locator strategy

- Locators **MUST** follow a robustness hierarchy, most-stable first: a dedicated test hook (for example `data-testid`) → element id → semantic/role selector → CSS → XPath as the last resort
- Position-based XPath (`//div[3]/span[2]`) **MUST NOT** be used; selectors **MUST** survive cosmetic markup changes

### Screenshot checkpoints

- Each test **MUST** capture at least one screenshot, and **MUST** capture the standard checkpoints where they apply: page-load, before a significant action, after it, and any visible error/validation state; a failure screenshot **MUST** be captured automatically by the harness on any test failure
- Screenshot names **MUST** begin with the test's TC-ID and end with a human-readable description of the visible state, so a screenshot is traceable on its filename alone

### Test protocol (audit trail)

- A run **MUST** be able to emit a machine-generated, human-readable protocol (default: Markdown) capturing run metadata (at least timestamp, commit, branch, browser/runtime), a pass/fail/skip summary, per-test results, the requirement coverage, and the screenshot gallery with descriptions
- Protocol output **MUST** be opt-in via a run flag and **MUST** be written to a timestamped, git-ignored location, so protocols accrete as history without entering version control
- The protocol **MUST** report, per requirement, how many tests are attributed to it

### Test markers and suites

- Each test **MUST** carry at least one marker classifying it (at minimum a smoke tier for "loads without crashing" and a core-behaviour tier), so a project can run fast subsets (`smoke`) independently of the full suite

### Assertions and preconditions

- Every assertion **MUST** carry a descriptive failure message that includes the TC-ID and the observed value; empty or tautological assertions (`assert True`, `assert page is not None`) are forbidden
- A missing precondition (absent seed data) **MUST** cause an explicit, reasoned skip—never a silent early return that lets a test pass without exercising anything
- Test-created data **MUST** use a unique suffix to stay isolated and reproducible across runs; session-scoped seed data **MUST** be idempotent (check-before-create)
- Preconditions **MUST** be established through the fastest reliable path (a seeded API call or fixture), and **not** by a click-through of the UI. A test drives through the browser only the interaction it asserts; provisioning precondition state (accounts, entities, navigation) via the UI multiplies runtime and couples unrelated flows into every test

### Spec traceability

- Every test **MUST** name, in its docstring/metadata, the TC-ID it realises and the requirement/spec case it traces to; the suite's TC-IDs and the requirement's TC-IDs **MAY** differ in numbering, in which case an explicit mapping **MUST** make the connection
- Traceability **MUST** be carried in the test artefacts themselves (docstrings, names, protocol coverage table); a separate machine-readable traceability index **MUST NOT** be emitted until a downstream reader declares the schema it needs

### Selenium + pytest reference profile (normative)

This profile is the binding realisation of the core for Python projects and the default the consuming agents assume when no other stack is declared. A project on another stack replaces this section wholesale but still satisfies the core above.

- The suite **MUST** live under `tests/e2e/` with: `conftest.py` (session fixtures, CLI options, idempotent seed data, marker registration), `protocol_plugin.py` (the protocol generator), `requirements.txt`, a `pages/` package with `base_page.py` plus one `<entity>_<view>_page.py` per page, and `test_<req>_<topic>.py` test modules grouped by requirement
- The browser fixture **MUST** be session-scoped, default to headless Chrome, support Firefox via a `--browser` option, and expose `--base-url` and `--generate-protocol` CLI options; the base URL **MUST** be a configurable option, never a hard-coded host. A project that must drop to a **per-test (function-scoped) browser** to avoid cross-test state bleed **MUST** document the reason and treat the extra per-test session allocation as a known cost to offset elsewhere: fewer journey-only E2E tests and API-provisioned preconditions rather than UI click-through
- `BasePage` **MUST** provide the waiting/interaction helpers (`navigate`, `wait_for_element`, `wait_for_element_visible`, `wait_for_element_clickable`, `wait_for_loading_complete`, `wait_for_url_contains`, framework-compatible field clear/fill); markers `smoke`, `core_crud`, `requires_auth` **MUST** be registered
- The reference templates shipped alongside this spec (`templates/`) are the canonical Gen-standard starting point; `e2e-test-generator` **MUST** treat them as the scaffold to adapt, and `e2e-test-reviewer` **MUST** treat them as the conformance baseline

### Consuming agents and skill

- `e2e-test-generator` **MUST** cite this spec, scaffold against the declared stack (defaulting to the reference profile), wire data-testid-first locators, screenshot checkpoints, markers, and protocol integration, and keep raw locator calls inside page objects only
- `e2e-test-reviewer` **MUST** review an existing suite against this spec's core (and the reference profile when that's the stack), report a checklist-based conformance verdict, and apply only minimal, surgical fixes rather than regenerating
- `e2e-result-reviewer` **MUST** read a run's protocol and screenshots and review them visually against the requirement/TC specs, returning prioritised findings; it **MUST NOT** edit code or tests (read-only)
- `test-pyramid-check` **MUST** audit tier completeness against `spec/project/test-pyramid-foundation/` and E2E discipline against this spec, returning a gap report; it **MUST NOT** generate or modify tests

## Acceptance Criteria

- [ ] Every binding requirement outside the reference-profile section is expressed without naming a concrete library, language, or runner
- [ ] The Selenium + pytest reference profile is complete enough that a Python project can scaffold a conformant suite from the shipped templates alone
- [ ] A scaffolded suite routes every UI interaction through page objects, uses only condition-based waits, follows the locator hierarchy, and carries markers, TC-ID docstrings, and descriptive assertions
- [ ] A run can emit a timestamped, git-ignored Markdown protocol with metadata, summary, per-requirement coverage, and a described screenshot gallery
- [ ] Each test names the TC-ID it realises and the requirement case it traces to; differing numbering is bridged by an explicit mapping
- [ ] `test-pyramid-check` reports present/missing tiers per feature and flags E2E-discipline violations
- [ ] `e2e-result-reviewer` runs read-only and produces prioritised findings keyed to requirement/TC IDs
- [ ] Each of the three agents and the skill cites this spec, and each `description` delimits it from the others and from `test-case-derivation` and `quality-gate`
- [ ] `test-case-derivation/{en,de}.md` no longer contradicts this spec: its boundary against E2E automation is drawn by responsibility, not by "shared vs. project-local"

## References

- [R1] Agent authoring rules the three agents conform to: `spec/claude/agent-management/`
- [R2] Skill authoring rules and the skill-vs-agent decision: `spec/claude/skill-management/`, `spec/claude/skill-vs-agent/`
- [R3] Abstract test-case derivation, delimited against this spec: `spec/project/test-case-derivation/`
- [R4] Fast-tier execution gate, delimited against this spec: `spec/project/quality-gate/`
- [R5] Page Object Model (background methodology): <https://martinfowler.com/bliki/PageObject.html>
- [R6] Test pyramid foundation (the tier model and taxonomy the E2E tier sits atop; owner of tier-completeness and coverage governance): `spec/project/test-pyramid-foundation/`
- [R7] `spec/project/behavior-driven-development/`: owns the BDD scenario/specification layer above these execution mechanics; its scenario steps delegate to this spec's page objects

## Open Questions

- Whether a second, equally normative Playwright/TypeScript reference profile should ship once a portfolio project needs it, or whether the Selenium profile plus the framework-neutral core is enough guidance for a non-Python stack. Provisional default until a consumer forces the question: ship only the Selenium profile and rely on the core for other stacks.
