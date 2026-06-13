# Test Tier: Component

Status: draft

## Context

The component tier sits **between unit and integration** in the pyramid defined by `spec/project/test-pyramid-foundation/`. It exercises a single **shippable component in isolation from its peers**: a whole component of collaborating units, with its real internal wiring intact, but with every *external* collaborator replaced by a test double at the component's boundary. It's slower than a unit test (seconds, not milliseconds) and broader (many units, not one), yet still isolated from real infrastructure, so it stays fast and deterministic enough to gate a pull request.

"Component test" names two distinct things depending on what the component is, and a tool-agnostic spec must treat both:

- a **frontend component test** renders a UI component and drives it as a user would, asserting on the observable output (the rendered DOM / accessibility tree);
- a **service / backend component test** drives a single service through its own external interface (its API), with all external services, third-party APIs, and often the datastore replaced by doubles at the process boundary.

This spec is the per-tier realisation of the foundation's **invariant shape** for the component tier. It fills every field that shape mandates and adds the tier-specific substance: the two flavours, the assert-observable-output rule for frontend, the service-through-its-own-interface model for backend, the in-process/out-of-process realism-versus-speed axis, and the boundary doubles.

It's deliberately **tool-agnostic**: the binding requirements never name a framework. Concrete tools appear only as an illustrative reference profile.

**Relationship to the other specs.** This tier is bounded by responsibility, not by overlap:

- `spec/project/test-pyramid-foundation/` [R1] owns the tier model and the Meszaros test-double taxonomy. This spec details the component tier; it doesn't restate the model.
- `spec/project/test-tier-unit/` [R2] is the tier **below**: one isolated unit with its collaborators doubled. The boundary is "one unit, collaborators mocked" (unit) vs "a whole component of collaborating units, real internal wiring, only externals doubled" (component).
- `spec/project/test-tier-integration/` [R3] is the tier **above**: it brings in a **real external collaborator**. The boundary is "externals stubbed at the boundary" (component) vs "one real external collaborator" (integration).
- `spec/project/quality-gate/` [R4] **executes** the component tier in CI and owns the run mechanics and output shape.
- For frontend components, the cross-cutting visual-regression and accessibility dimensions attach at this tier (see §"Cross-cutting at component scope"); deep web-UI review remains `spec/frontend/webview-ui-optimization/`.

Readers: spec authors writing the sibling per-tier specs; skill and agent authors building the component-tier development/execution/analysis triad; frontend and backend developers writing component tests; reviewers checking that a component test asserts observable behaviour, doubles only externals, and is deterministic.

## Goals

- Define the component tier as a single shippable component in isolation, and separate its two flavours (frontend, service) without forcing one model onto the other
- For frontend, require assertions on **observable output through user-facing queries**, never on internal state or instances
- For backend, require driving the service through its **own external interface** with externals doubled at the boundary
- Make the **in-process vs out-of-process** realism/speed trade-off an explicit, recorded choice
- Pin the boundaries against the Unit tier (one isolated unit) and the Integration tier (a real external collaborator)
- Keep the tier tool-agnostic, with a swappable reference profile rather than a mandated framework

## Non-Goals

- Executing the tier or defining its run mechanics and output table: owned by `spec/project/quality-gate/` [R4]
- Bringing in a **real external collaborator** (live service, real database over the network): that crosses into the Integration tier
- Testing one isolated unit with mocked collaborators: that's the Unit tier
- Driving the whole running system end to end through its user surface: that's the E2E tier (`spec/project/e2e-test-automation/`)
- Mandating a specific component-test framework or service-virtualization tool: the reference profile is illustrative
- Defining the deep web-UI performance / security / i18n review: owned by `spec/frontend/webview-ui-optimization/`

## Requirements

### Purpose and scope boundary

- **MUST** define a component test as one that exercises a **single shippable component of collaborating units with its real internal wiring**, isolated from its peers by replacing every external collaborator with a test double at the component boundary [R10].
- **MUST** keep the boundary to the **Unit tier** sharp: a unit test exercises one isolated unit (collaborators absent or mocked); a component test exercises the whole component with real internal wiring. A behaviour determinable from a single unit belongs below this tier [R2], [R10].
- **MUST** keep the boundary to the **Integration tier** sharp: at the component tier every external collaborator is **doubled** at the boundary; the moment a test exercises a **real** external collaborator it's an integration test [R3], [R10].
- **MUST** assert on the component's **observable behaviour through its public surface** (rendered output for frontend, API responses and emitted events for backend), never on internal implementation detail [R5], [R7].

### Two flavours: Frontend component and service component

- **MUST** recognise the two flavours as distinct realisations of the same tier and let a project apply the one matching the component under test: a **frontend** UI component test and a **service / backend** component test.
- **MUST** apply the flavour-specific requirements below to the matching flavour, while both share the boundary, isolation, determinism, and placement requirements of this tier.

### Frontend component tests: Assert observable output, not internals

- **MUST** anchor frontend component testing in the guiding principle *"the more your tests resemble the way your software is used, the more confidence they can give you"* [R5], [R6]: tests render the component and assert on what a user can observe.
- **MUST** work with the **rendered output (DOM / accessibility tree), not component instances**, and **MUST NOT** assert on internal state, private methods, or instance internals; testing implementation details produces **both** false negatives (brittle breakage on a behaviour-preserving refactor) **and** false positives (a test that passes while the component is broken) [R7], [R8].
- **MUST NOT** use **shallow rendering** that stubs out a component's children to inspect internals; it tests the implementation, not the behaviour [R15].
- **MUST** treat **snapshot testing** as a narrow tool, not a default: a large automatically generated snapshot asserts nothing specific, is rubber-stamped on update, and is the documented snapshot-overuse anti-pattern [R14]; prefer explicit assertions on the specific observable output.

### Frontend query priority and the two legitimate users

- **MUST** select elements with **user-facing queries in priority order**: by role, then label, placeholder, text, or display value—and reserve a test-id query as the **last resort** when no user-perceivable handle exists [R5], [R9].
- **MUST** treat a UI component as having exactly **two legitimate users**: the **end-user** (who interacts with the rendered output) and the **developer** (who renders it via props)—and write tests only from those two vantage points, never through a synthetic "test user" that reaches into internal state [R6].

### Service component tests: The service through its own interface

- **MUST** define a service component test as one that **drives a single service through its own external interface (its API)** from a consumer's perspective, with all external collaborators (other services, third-party APIs, and often the datastore) replaced by test doubles at the process boundary [R10].
- **MUST** use the component's **own internal interfaces only to configure or probe** the test double environment (seed data, set up stub responses), not to bypass the service's public contract under test [R10].
- **SHOULD** use **service virtualization** (a stub of upstream services that returns canned, configurable responses at the network or in-memory boundary) to isolate the service from its real external dependencies [R12].

### In-process versus out-of-process (the realism/speed axis)

- **MUST** make the **in-process vs out-of-process** choice an explicit, recorded decision [R10]:
  - **In-process**: the service is instantiated in memory with in-memory doubles and datastores, no network is touched: faster and simpler, but less realistic because it bypasses real serialisation and wiring, and it needs a test-mode artefact.
  - **Out-of-process**: the service runs as a separately deployed process exercised over its real transport with externals still doubled: more realistic (real network, serialisation) but slower with more moving parts.
- **SHOULD** prefer **in-process** for the fast feedback the tier is meant to give, and reserve **out-of-process** for components whose transport/serialisation behaviour is itself part of the contract under test.

### Isolation and permitted test doubles

- **MUST** keep **real**: the component's own code and its internal wiring; **MUST** double: every external collaborator (other services, third-party APIs, network, and—where realism doesn't require it—the datastore), using the foundation's **Meszaros vocabulary** (dummy, fake, stub, spy, mock) and stating which kind each double is [R1], [R11].
- **MAY** use a **fake** (for example an in-memory datastore) in place of a real store when the store isn't the realism the test needs; a test that requires the **real** store crosses into the Integration tier [R3], [R11].

### Determinism, speed, and placement

- **MUST** keep the tier **deterministic**: control time, randomness, and all network interaction (every external call is doubled), so a component test never flakes on real-world weather, per the foundation.
- **MUST** accept that component tests are **slower than unit tests (seconds)** but **MUST** keep them isolated from real infrastructure so they stay fast enough to **gate a pull request** in CI; the fast ones **MAY** also run pre-commit.

### Cross-cutting at component scope

- **MUST** treat **visual-regression** and **accessibility (a11y)** checks as the foundation's cross-cutting dimensions applied *at* component scope (asserting on the same rendered output), not as a separate tier; a component test **MAY** carry an a11y assertion or a visual-snapshot baseline against the rendered component.
- **MUST** keep the boundary to `spec/frontend/webview-ui-optimization/` (deep web-UI performance / security / i18n review) intact: that review is a distinct, broader concern, not the component tier.

### Anti-patterns

- **MUST** reject, as canonical anti-patterns: asserting on internal state/instances; shallow rendering; snapshot overuse; brittle implementation-coupled selectors; standing up a **real** external collaborator (that's integration); an over-broad component boundary that swallows several components; and flaky components from uncontrolled time or network.

### Traceability

- **MUST** let a component test that verifies a derived test case name the **TC-ID** (and through it the requirement) it covers, per the foundation's traceability chain, so requirement coverage is auditable.

### Optional reference profile

- **MAY** pin a fully worked, stack-specific reference profile, clearly demoted to "reference." Illustrative frontend profile: a Testing-Library-family renderer (React/Vue/Svelte Testing Library) with user-event interaction and role-first queries, optionally Storybook play functions for interaction, run under Vitest. Illustrative backend profile: an in-process service harness (for example a framework test client such as Starlette/FastAPI `TestClient` or a Spring Boot slice) with a service-virtualization stub (for example WireMock) for externals. Tool names are illustrative, never required.

## Acceptance Criteria

- [ ] The spec defines the component tier as a single shippable component in isolation (real internal wiring, externals doubled) and names both flavours (frontend, service)
- [ ] The boundary against the Unit tier (one isolated unit vs a whole component) and the Integration tier (externals doubled vs a real external collaborator) is explicit and cited
- [ ] Frontend tests are required to assert on rendered output (DOM / accessibility tree), forbidden from asserting on internals, with the false-negative + false-positive rationale and the no-shallow-rendering rule
- [ ] The user-facing query priority (role first, test-id last resort) and the two-legitimate-users model are required, cited to Testing Library / Dodds
- [ ] Snapshot testing is bound as a narrow tool with the overuse anti-pattern named
- [ ] Service component tests are required to drive the service through its own interface with externals doubled, with internal interfaces used only to configure/probe, cited to Fowler/Clemson
- [ ] The in-process vs out-of-process realism/speed trade-off is an explicit recorded choice
- [ ] Isolation keeps the component real and doubles externals using the Meszaros vocabulary; a real datastore is declared as crossing into integration
- [ ] Determinism (controlled time/randomness/network) and placement (PR-gating CI, fast ones pre-commit) are required
- [ ] Visual-regression and accessibility are placed as cross-cutting at component scope, bounded against `webview-ui-optimization`
- [ ] Traceability to TC-ID is required, and an optional clearly-demoted reference profile (frontend + backend) is provided without mandating a framework
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-pyramid-foundation/`: the tier model and Meszaros test-double taxonomy this spec realises
- [R2] `spec/project/test-tier-unit/`: the tier below (one isolated unit, collaborators mocked); the unit↔component boundary
- [R3] `spec/project/test-tier-integration/`: the tier above (a real external collaborator); the component↔integration boundary
- [R4] `spec/project/quality-gate/`: executes the component tier in CI and owns the run mechanics / output shape
- [R5] Testing Library, *Guiding Principles* (resemble real usage; query priority): <https://testing-library.com/docs/guiding-principles/>
- [R6] Kent C. Dodds, *Avoid the Test User* (the two legitimate users of a component): <https://kentcdodds.com/blog/avoid-the-test-user>
- [R7] Kent C. Dodds, *Testing Implementation Details* (false negatives and false positives): <https://kentcdodds.com/blog/testing-implementation-details>
- [R8] Kent C. Dodds, *Introducing the React Testing Library* (test DOM nodes, not instances): <https://kentcdodds.com/blog/introducing-the-react-testing-library>
- [R9] Testing Library, *About Queries* (priority order, test-id as last resort): <https://testing-library.com/docs/queries/about/>
- [R10] M. Fowler & T. Clemson, *Testing Strategies in a Microservice Architecture* (component test definition; in-process vs out-of-process): <https://martinfowler.com/articles/microservice-testing/>
- [R11] Martin Fowler, *Mocks Aren't Stubs* (the five Meszaros doubles): <https://martinfowler.com/articles/mocksArentStubs.html>
- [R12] WireMock, *Service Virtualization* (stub upstream services at the boundary): <https://wiremock.org/docs/solutions/service-virtualization/>
- [R13] Storybook, *Interaction Testing* (play functions): <https://storybook.js.org/docs/writing-tests/interaction-testing>
- [R14] Jest, *Snapshot Testing* (where it helps; the overuse caveat): <https://jestjs.io/docs/snapshot-testing>
- [R15] Kent C. Dodds, *Why I Never Use Shallow Rendering*: <https://kentcdodds.com/blog/why-i-never-use-shallow-rendering>

## Open Questions

- Should the portfolio require a frontend component's a11y assertion as a default (every rendered component carries at least one accessibility check), or keep it opt-in as a cross-cutting addition?
- For backend services, should the portfolio default to in-process component tests and require an explicit justification for out-of-process, or leave the axis fully per-project?
- Does the component tier's develop/execute/analyse triad warrant flavour-specific agents (a frontend component-test author distinct from a service component-test author), or one component-tier author with a flavour parameter?
- Where a component test carries a visual-regression baseline, does the baseline artefact live with the test, and how's its review bound against `webview-ui-optimization`?
