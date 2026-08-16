# Test Tier: Unit

Status: draft

## Context

The unit tier is the **broad, fast base of executing tests** in the pyramid defined by `spec/project/test-pyramid-foundation/`: it's the first tier that actually runs the code (unlike static analysis below it, which only reads code shape) and the one that gives the cheapest, most precise failure localisation. A unit test exercises one small unit of behaviour and asserts the observable outcome, in milliseconds, with no contact with the outside world.

This spec is the per-tier realisation of the foundation's **invariant shape** for the unit tier. It fills every field that shape mandates (purpose and scope boundary, isolation and permitted test doubles, speed and determinism, execution placement, traceability, canonical anti-patterns, optional reference profile) and adds the tier-specific substance: the deliberately team-determined definition of "a unit," the solitary/sociable and classicist/mockist distinctions, the FIRST properties, the assert-behaviour-not-implementation rule, and the place of property-based testing.

It's deliberately **tool-agnostic**: the binding requirements never name a runner or mocking library. Concrete tools appear only as an illustrative reference profile.

**Relationship to the other specs.** This tier is bounded by responsibility, not by overlap:

- `spec/project/test-pyramid-foundation/` [R1] owns the tier model, the FIRST-adjacent governance invariants, and the Meszaros test-double taxonomy. This spec details the unit tier; it doesn't restate the model.
- `spec/project/test-tier-static-analysis/` [R2] is the tier **below**: it analyses code without executing it. The boundary is "reads code shape" (static) vs "runs the unit and asserts behaviour" (unit).
- The **Component tier** (`spec/project/test-tier-component/`, sibling, above) exercises a whole shippable component; the **Integration tier** (`spec/project/test-tier-integration/`, above) brings in a real external collaborator. The boundary is "one isolated unit" (this tier) vs "a component / collaborating units with real dependencies."
- `spec/project/quality-gate/` [R3] **executes** the unit tier as part of the fast gate and owns the run mechanics and output shape. This spec defines what the unit tier must contain; quality-gate defines how it's run.

Readers: spec authors writing the sibling per-tier specs; skill and agent authors building the unit-tier development/execution/analysis triad; developers writing and reviewing unit tests; reviewers checking that a unit suite is fast, isolated, behaviour-asserting, and not over-mocked.

## Goals

- Define what a unit test verifies and, sharply, what turns it into a different tier (crossing the I/O line, pulling in real collaborators)
- Anchor the deliberately team-determined definition of "a unit" and the solitary/sociable and classicist/mockist choices, so a project picks a consistent style on purpose
- Encode the FIRST properties (Fast, Isolated, Repeatable, Self-validating, Timely) as the tier's quality bar
- Require assertions on **observable behaviour through the public interface**, never on private implementation detail, so tests survive refactoring
- Bound test-double usage so the tier doesn't drift into over-mocking that couples tests to implementation
- Keep the tier tool-agnostic, with a swappable reference profile rather than a mandated runner

## Non-Goals

- Executing the tier or defining its run mechanics and output table: owned by `spec/project/quality-gate/` [R3]
- Exercising real external collaborators (database, network, filesystem, broker): that crosses into the Integration tier
- Testing a whole shippable component through its own interface: that's the Component tier
- Mandating a specific test runner, assertion library, or mocking framework: the reference profile is illustrative
- Prescribing a numeric coverage target: coverage is a guide per the foundation, not a unit-tier gate
- Requiring test-driven development: TDD is a recommended practice for producing unit tests, not a precondition for the tier

## Requirements

### Purpose and scope boundary

- **MUST** define a unit test as one that **executes a single unit of behaviour and asserts the observable outcome**, with precise failure localisation, as the broad fast base of the executing tiers [R1], [R5].
- **MUST NOT** let a unit test touch the **outside world**: no real database, filesystem, network, system clock, or source of randomness. Crossing that line makes the test an integration test, not a unit test, regardless of what it's labelled [R5], [R9].
- **MUST** keep the boundary to **static analysis** sharp: static analysis reads code shape without running it; the unit tier runs the unit. A check that needs no execution belongs below this tier [R2].
- **MUST** keep the boundary to the **Component and Integration tiers** sharp: a unit test covers one isolated unit, not a whole shippable component and not a real external collaborator.

### What "a unit" is, and solitary versus sociable

- **MUST** treat the definition of "a unit" as **deliberately team-determined**: a unit may be a single function, a class, or a small cluster of related objects, decided per project and recorded, rather than dictated portfolio-wide [R5].
- **MUST** let a project choose between **solitary** unit tests (the unit is isolated from its collaborators with test doubles) and **sociable** unit tests (the unit exercises its real collaborators), and record which style is the default; Fowler notes both are legitimate and that classicists tend to prefer sociable [R5].
- **SHOULD** prefer **sociable** tests where the real collaborators are themselves fast and deterministic (in-process, no I/O), because they couple the test less to internal structure and still satisfy FIRST; reach for solitary isolation when a collaborator is slow, non-deterministic, or not yet built [R5].

### The classicist and mockist schools

- **MUST** recognise the two schools as a deliberate choice, not an accident: the **classicist** (Detroit / Chicago, state-based, real collaborators, sociable) and the **mockist** (London, interaction-based, mocked collaborators, solitary, outside-in) [R5], [R6].
- **MUST** record that **mockist / interaction-based** tests verify *how* collaborators were called and are therefore more **coupled to implementation and more refactor-fragile**; a project adopting them accepts that trade for stronger isolation and outside-in design pressure [R5], [R6].

### FIRST properties

- **MUST** require unit tests to satisfy the **FIRST** properties (Ottinger & Schuchert) [R9], [R10]:
  - **Fast**: runs in milliseconds, so the whole suite gives feedback in seconds and developers run it constantly.
  - **Isolated / Independent**: no dependence on other tests, on ordering, or on shared mutable state; each sets up and tears down its own world.
  - **Repeatable**: same result every run, in any environment; achieved by removing I/O and external state.
  - **Self-validating**: passes or fails on its own with a clear assertion; no human inspection of output.
  - **Timely**: written close to the code under test (the TDD ideal of before, but at minimum alongside, never long after).

### Isolation and permitted test doubles

- **MUST** use the foundation's **Meszaros test-double vocabulary** (dummy, fake, stub, spy, mock) and state which kind a given double is, so reviews speak one language [R1], [R7].
- **MUST** prefer **state verification** (assert the resulting state) and reserve **behaviour verification** (mocks asserting interactions) for the cases where the interaction *is* the observable contract; over-using behaviour verification is the over-mocking smell [R6], [R7].
- **MUST NOT** **over-mock**: mock only collaborators the project owns and that represent a real boundary; don't mock value objects, don't mock types you don't own, and don't replace so much of the unit's world that the test only asserts its own scaffolding [R7], [R8].
- **MUST** apply the foundation's fidelity rule [R1] to this tier's collaborator doubles, exemption included, rather than restating it. The three rules above bound *how much* a unit test doubles; this one bounds whether the double can **refuse**, and at this tier the recurring offender is a hand-written double of a **persistence or repository boundary**: the real collaborator generates or discards keys, enforces uniqueness, and rejects nulls, while the double silently does none of it and every test in the file then passes for a state the database would never hold. Where the divergence can't be closed, it **MUST** be named in the double itself [R1], and the resulting failure mode is citable as `T9` per [R12].

### What to assert

- **MUST** assert **observable behaviour through the unit's public interface**, never private implementation detail; a test that knows how the unit works internally breaks on refactoring that preserves behaviour, which is the canonical fragile-test cause [R8].
- **MUST** structure each test as **Arrange–Act–Assert** (Given–When–Then): set up, exercise one behaviour, assert the outcome.
- **MUST** assert **one logical behaviour per test** and give it an **intention-revealing name** stating the behaviour and expected outcome, not the method under test.
- **MUST** keep tests **independent**: no ordering dependency, no shared mutable fixture, per the foundation's determinism rule.

### Property-based and parameterized testing

- **SHOULD** use **parameterized / table-driven** tests to cover a behaviour across many inputs without duplicating test bodies.
- **MAY** use **property-based testing** (asserting invariants over generated inputs, shrinking failures to a minimal case) at the unit tier where a behaviour is best expressed as a property rather than a fixed example [R11]; property-based tests **MUST** still be deterministic in the foundation's sense (a fixed seed reproduces a failure).

### Determinism, speed, and placement

- **MUST** keep the tier **deterministic and fast**: a flaky or slow "unit" test is a defect; the usual cause is hidden I/O, time, randomness, or order dependence, all of which the tier forbids [R5], [R9].
- **MUST** run the unit tier in **pre-commit and as a PR-gating CI check** (the fast-tier gate per `spec/project/pull-request-workflow/`, executed per `spec/project/quality-gate/`), because it's cheap enough to gate every change.

### Coverage and suite quality

- **MUST** treat unit **coverage as a guide, not a target**, per the foundation: high line coverage with weak assertions is a false signal, and **mutation score** is the stronger measure of whether the unit tests actually catch behavioural changes.
- **SHOULD** write the test at the **lowest tier that gives confidence** (the foundation's rule): a behaviour fully determinable from one unit belongs here, not in a slower higher tier.

### Traceability

- **MUST** let a unit test that verifies a derived test case name the **TC-ID** (and through it the requirement) it covers, per the foundation's traceability chain, so requirement coverage is auditable; purely internal units that trace to no requirement need no TC-ID but **SHOULD** still carry an intention-revealing name.

### Optional reference profile

- **MAY** pin a fully worked, stack-specific reference profile, clearly demoted to "reference." An illustrative Python profile: `pytest` as the runner (with parameterized fixtures), `unittest.mock` for the rare owned-boundary double, and `Hypothesis` for property-based invariants. Other ecosystems realise the same tier with their own tools (JUnit/TestNG + Mockito; Vitest/Jest + Sinon + fast-check; Go's `testing`; Rust's `cargo test`). Tool names are illustrative, never required.

## Acceptance Criteria

- [ ] The spec defines a unit test as single-behaviour execution with no outside-world contact, and declares that crossing the I/O line makes it an integration test
- [ ] "A unit" is established as team-determined, and the solitary/sociable choice is required to be recorded, cited to Fowler
- [ ] The classicist and mockist schools are described with the implementation-coupling / refactor-fragility trade-off of interaction-based tests
- [ ] The FIRST properties are enumerated with each property's meaning, attributed to Ottinger & Schuchert
- [ ] Test doubles use the foundation's Meszaros vocabulary, state verification is preferred, and over-mocking is forbidden with the mock-only-what-you-own rule
- [ ] The foundation's fidelity rule is applied to this tier's doubles by reference rather than restated, the persistence boundary is named as the recurring offender here, and the exemption stays the foundation's two-part one
- [ ] Assertions are required on observable behaviour through the public interface, with AAA, one-behaviour-per-test, intention-revealing names, and independence
- [ ] Parameterized testing is recommended and property-based testing is permitted with a determinism (fixed-seed) constraint
- [ ] Determinism and speed are required, the flaky/slow-unit causes are named, and the tier is placed in pre-commit + PR gate
- [ ] Coverage is bound as a guide with mutation score as the stronger signal, and the lowest-tier-that-gives-confidence rule is referenced
- [ ] Traceability to TC-ID is required for requirement-verifying units
- [ ] The delimitation against static analysis (below), component/integration (above), and quality-gate (executes) is explicit
- [ ] An optional, clearly-demoted reference profile is provided without mandating a toolchain
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-pyramid-foundation/`: the tier model, FIRST-adjacent governance, and Meszaros test-double taxonomy this spec realises
- [R2] `spec/project/test-tier-static-analysis/`: the tier below (analyses code without executing it); the static↔unit boundary
- [R3] `spec/project/quality-gate/`: executes the unit tier in the fast gate and owns the run mechanics / output shape
- [R4] `spec/project/pull-request-workflow/`: owns the required-status-check enforcement the unit-tier gate feeds
- [R5] Martin Fowler, *UnitTest* (team-determined unit; solitary vs sociable; classicist vs mockist): <https://martinfowler.com/bliki/UnitTest.html>
- [R6] Martin Fowler, *Mocks Aren't Stubs* (state vs behaviour verification; mockist coupling): <https://martinfowler.com/articles/mocksArentStubs.html>
- [R7] Martin Fowler, *TestDouble* (the five doubles; over-mocking): <https://martinfowler.com/bliki/TestDouble.html>
- [R8] Kent C. Dodds, *Testing Implementation Details* (assert behaviour, not internals): <https://kentcdodds.com/blog/testing-implementation-details>
- [R9] T. Ottinger & B. Schuchert, *FIRST* (Fast, Isolated, Repeatable, Self-validating, Timely): <http://agileinaflash.blogspot.com/2009/02/first.html>
- [R10] T. Ottinger, *Brett Schuchert and I came up with FIRST* (authoritative attribution): <https://medium.com/@tottinge_79838/brett-schuchert-and-i-came-up-with-first-so-this-is-an-authoritative-statement-ec6006f6a59e>
- [R11] *fast-check*: property-based testing (invariants over generated inputs, shrinking): <https://fast-check.dev/>
- [R12] `spec/project/test-falsifiability/`: the cross-tier taxonomy of tests that can't fail; `T9` is the failure mode a double more permissive than its collaborator produces, and the spec carries the review question that detects it

## Open Questions

- Should the portfolio default a project's unit style (sociable/classicist vs solitary/mockist), or leave it per-project with only the "record your choice" requirement?
- Does the unit tier's develop/execute/analyse triad need a dedicated unit-test-author agent and an over-mocking reviewer, or does `quality-gate` (execute) plus a thin author capability suffice—and should an over-mocking/implementation-detail review be a distinct agent or a check inside a broader test reviewer?
- Should property-based testing be elevated from MAY to SHOULD for pure functions with clear invariants, or stay optional?
