# Test Tier: Integration

Status: draft

## Context

The integration tier sits **above the component tier** in the pyramid defined by `spec/project/test-pyramid-foundation/`. It's the first tier that exercises code against a **real external collaborator**: a real database, message broker, filesystem, or a single other service—rather than a double. Where a component test replaces *every* external with a double at the boundary, an integration test lets the code talk to exactly **one** real collaborator through a real connection, and verifies the **integration seam**: the place where the code serialises, queries, maps, or speaks a wire protocol to the outside.

The word "integration test" is dangerously ambiguous, and this spec resolves it. A **narrow** integration test exercises only the code that talks to one separate collaborator, is no larger than a unit test, runs under the unit framework, and doubles everything else. A **broad** integration test stands up many live services together and is really a system test in disguise; Thoughtworks' Technology Radar places broad integration tests and shared enterprise-wide test environments on **hold** as expensive, fragile, slow bottlenecks that give false confidence and un-localisable failures. This spec **mandates the narrow form** and treats broad integration as discouraged.

This spec is the per-tier realisation of the foundation's **invariant shape** for the integration tier. It fills every field that shape mandates and adds the tier-specific substance: the narrow/broad distinction, the seam-only assertion scope, real-but-ephemeral collaborators (over unfaithful in-memory fakes), determinism despite real systems, and the boundary to the contract tier.

It's deliberately **tool-agnostic**: the binding requirements never name a tool. Concrete tools appear only as an illustrative reference profile.

**Relationship to the other specs.** This tier is bounded by responsibility, not by overlap:

- `spec/project/test-pyramid-foundation/` [R1] owns the tier model and the Meszaros test-double taxonomy. This spec details the integration tier; it doesn't restate the model.
- `spec/project/test-tier-component/` [R2] is the tier **below**: *every* external collaborator is doubled. The boundary is "all externals doubled" (component) vs "exactly one real external collaborator, the rest doubled" (integration).
- `spec/project/test-tier-contract/` [R3] is the **sibling above/beside**: it verifies a cross-service agreement *without standing up both sides*. The boundary is "a real collaborator you own and release in lockstep with" (integration) vs "a collaborator released independently of you, or one you don't own at all" (contract). The release boundary, not ownership, is what decides it.
- `spec/project/e2e-test-automation/` [R4] is the system tier: many real collaborators, the whole running system. The boundary is "one seam" (integration) vs "the whole system end to end" (E2E).
- `spec/project/quality-gate/` [R5] **executes** the fast integration tests and owns the run mechanics and output shape.

Readers: spec authors writing the sibling per-tier specs; skill and agent authors building the integration-tier development/execution/analysis triad; developers writing integration tests against databases, brokers, and services; reviewers checking that an integration test is narrow, seam-focused, ephemeral, and deterministic.

## Goals

- Mandate the **narrow** integration test and mark broad integration (many live services) as discouraged
- Scope assertions to the **integration seam** (serialisation, real queries against a real schema, mapping, connection, wire protocol, transactions, migrations), never business logic or whole-system journeys
- Require **real but ephemeral** collaborators (disposable containers) over unfaithful in-memory substitutes that drift from production technology
- Keep the tier deterministic despite real systems, via ephemeral environments and per-test data isolation
- Draw a crisp boundary to the **contract** tier (a real owned collaborator vs a cross-service agreement) and to E2E (one seam vs the whole system)
- Keep the tier tool-agnostic, with a swappable reference profile rather than a mandated tool

## Non-Goals

- Executing the tier or defining its run mechanics and output table: owned by `spec/project/quality-gate/` [R5]
- Standing up **many** live services together (broad integration / system testing): discouraged here and, at full breadth, owned by the E2E tier [R4]
- Re-testing business logic determinable at the **unit** tier: that's duplication, not integration
- Verifying a **cross-service agreement** without a live partner: that's the contract tier [R3]
- Doubling the collaborator under test: an integration test exercises a **real** collaborator (a doubled one would make it a component test)
- Mandating a specific container, database, or broker tool: the reference profile is illustrative

## Requirements

### Purpose and scope boundary

- **MUST** define the default integration test as **narrow**: it exercises only the code that talks to **one** separate real collaborator, is no larger than a unit test, runs under the unit framework, and doubles every other external [R6], [R7].
- **MUST** treat **broad** integration tests (many live services stood up together) as **discouraged**: they're expensive, slow, fragile, and give un-localisable failures, and Thoughtworks' Technology Radar holds them and shared enterprise-wide test environments [R8], [R9]. Breadth at the level of the whole system belongs to the E2E tier, not here.
- **MUST** keep the boundary to the **component tier** sharp: a component test doubles *every* external; an integration test exercises exactly **one** real external collaborator while doubling the rest [R2].
- **MUST** exercise a collaborator the project **owns and releases in lockstep with** (its own database, broker, or a single owned service deployed and versioned together with the code under test); cross-service agreements with a partner the project doesn't control belong to the contract tier [R3], [R10].
- **MUST** apply the following **decision rule** when the collaborator is a service the project owns but **deploys separately**: the seam is an **integration** test when the same team deploys *and* versions both sides together, so the two can only be in production in a combination the team chose; it's a **contract** test as soon as either side can be released independently of the other, even under one owner. Ownership isn't the discriminator—the **release boundary** is. Where the sides ship independently, the live failure mode is version skew between a producer and a consumer that were never released together, and a live integration test can't observe it: it exercises one deployed pair while production may hold any other. The contract tier's broker plus `can-i-deploy` gate is built for exactly that [R3]. Where the sides ship together, the skew can't arise, and a real collaborator gives higher fidelity at lower ceremony.

### What an integration test verifies, and what it must not

- **MUST** scope assertions to the **integration seam**: the points where the code serialises or deserialises data and crosses a boundary—real SQL/queries against a real schema, object-relational mapping, connection and transaction handling, wire protocols, message formats, and schema-migration correctness [R6], [R7].
- **MUST NOT** re-test **business logic** that's determinable at the unit tier; duplicating unit-tier behaviour at the slow integration tier is waste, not coverage [R7].
- **MUST NOT** drive **whole-system user journeys**; that's the E2E tier. An integration test covers one seam, not an end-to-end path [R4], [R6].

### Real but ephemeral collaborators

- **MUST** run the integration test against the **real technology**, provisioned as a **disposable, ephemeral** instance (for example a real database or broker in a throwaway container) per test or per suite, so the test has production fidelity without a shared, long-lived environment [R11].
- **MUST NOT** substitute an **in-memory fake** that behaves differently from the production technology (for example an embedded H2 database standing in for PostgreSQL): dialect and behaviour drift produces false confidence—a query that passes against the fake can fail against the real engine [R11].
- **MUST NOT** depend on a **shared, mutable, long-lived** test environment (a central staging database every test hits): shared mutable state is the dominant flakiness and bottleneck source at this tier; each test owns its ephemeral collaborator [R8], [R9].

### Isolation level and permitted doubles

- **MUST** keep **real** exactly **one** external collaborator (the one under test) and keep **doubled**, using the foundation's Meszaros vocabulary, every *other* external the code touches, so the test localises failures to the single seam it covers [R1], [R6].
- **MUST** state, for each integration test, which collaborator is real and which are doubled, so a reviewer can confirm the test is narrow.
- **MUST NOT** let any of those *other*, legitimately doubled externals be **more permissive than what it replaces** along any dimension the test relies on, per the foundation's fidelity rule [R1]. This is distinct from the in-memory-fake ban above, which governs the **one real collaborator** seam and forbids substituting production technology there at all; here the collaborators are correctly doubled, and the requirement is that each still **refuses** what the real one refuses. A narrow test earns its precise failure localisation from the real seam it covers, and gains nothing from it if a doubled neighbour accepts a call production would reject. Where the divergence can't be closed, it **MUST** be named in the double itself [R1]; the resulting failure mode is citable as `T9` per [R13].

### Determinism and test-data isolation

- **MUST** keep the tier **deterministic** despite using real systems: fresh schema and seeded data per run, **per-test data isolation** (transaction rollback, truncation, or a fresh ephemeral instance between tests), no ordering dependency, and controlled time—so a real database or broker never makes the test flaky.
- **MUST** remove the flakiness sources specific to this tier—shared state, test ordering, network weather, and container-startup races—by waiting on readiness conditions (not fixed sleeps) and isolating each test's data; larger tests are empirically more flake-prone, which is a further reason to keep them narrow and few [R12].

### Speed and placement

- **MUST** accept that integration tests are **slower** than unit and component tests (seconds to minutes, including container startup) and therefore **fewer**, per the pyramid's economics.
- **MUST** gate a pull request on the **fast narrow** integration tests (executed per `spec/project/quality-gate/`, declared as required checks per `spec/project/pull-request-workflow/`), because the apex `spec/project/test-pyramid-foundation/` §CI gating model—the authority on which tiers belong in the gate—classes narrow integration among the fast tiers that MUST gate; run slower or heavier integration tests in a dedicated CI stage or nightly rather than blocking every change.

### Boundary to the contract tier

- **MUST** route a **service-to-service** agreement to the **contract tier** rather than a broad integration test: a consumer-driven contract test verifies that the doubles a consumer uses return the same shape the real provider produces, **without standing up both sides live** [R3], [R10].
- **MUST NOT** hit a **real third-party production API** in an integration test: use a sandbox, a service-virtualization stub, or push the verification to the contract tier—never the live partner's production system.

### Anti-patterns

- **MUST** reject, as canonical anti-patterns: broad integration as the default; a shared mutable staging/test database hit by all tests; re-testing unit-tier business logic; in-memory substitutes that don't match production technology (false confidence); flaky tests from shared state, ordering, or container races; and hitting real third-party production APIs.

### Traceability

- **MUST** let an integration test that verifies a derived test case name the **TC-ID** (and through it the requirement) it covers, per the foundation's traceability chain, so requirement coverage is auditable.

### Optional reference profile

- **MAY** pin a fully worked, stack-specific reference profile, clearly demoted to "reference." An illustrative profile: a Testcontainers-style harness that starts the **real** database or broker in a disposable container, applies the project's real migrations, seeds per-test data, and tears down after the suite; for an unavoidable third-party dependency, a sandbox endpoint or a service-virtualization stub rather than the live production service. Testcontainers exists for the major ecosystems (Java/Python/Go/Node/.NET); tool names are illustrative, never required.

## Acceptance Criteria

- [ ] The spec mandates narrow integration tests and marks broad integration (many live services) as discouraged, cited to Fowler and the Thoughtworks Radar hold
- [ ] Assertions are scoped to the integration seam (serialisation, real queries/schema, mapping, connection, transactions, migrations) and forbidden from re-testing unit-tier business logic or driving whole-system journeys
- [ ] Real-but-ephemeral collaborators are required, in-memory fakes that drift from production technology are forbidden (with the H2-vs-real-database example), and shared long-lived test environments are forbidden
- [ ] The isolation level is exactly one real external collaborator with all others doubled, contrasted explicitly with the component tier (all doubled)
- [ ] The doubled neighbours are forbidden from being more permissive than what they replace, the rule is delimited against the in-memory-fake ban that governs the one real seam, and a divergence that can't be closed must be declared in the double
- [ ] Determinism via ephemeral environments + per-test data isolation is required, the tier-specific flakiness sources are named, and readiness-condition waits (not sleeps) are required
- [ ] The tier is placed as slower/fewer, with fast narrow tests gating the PR and heavier ones in a dedicated stage / nightly
- [ ] The boundary to the contract tier (a real owned collaborator vs a cross-service agreement verified without both sides live) is crisp, drawn by the release boundary rather than by ownership via an explicit decision rule for an owned-but-separately-deployed service, and hitting a real third-party production API is forbidden
- [ ] The boundary to E2E (one seam vs the whole system) is explicit
- [ ] Traceability to TC-ID is required
- [ ] An optional, clearly-demoted reference profile (real dependency in a disposable container + migrations + per-test seed) is provided without mandating a tool
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-pyramid-foundation/`: the tier model and Meszaros test-double taxonomy this spec realises
- [R2] `spec/project/test-tier-component/`: the tier below (all externals doubled); the component↔integration boundary
- [R3] `spec/project/test-tier-contract/`: the sibling tier (a cross-service agreement without both sides live); the integration↔contract boundary
- [R4] `spec/project/e2e-test-automation/`: the system tier (the whole running system); the integration↔E2E boundary
- [R5] `spec/project/quality-gate/`: executes the fast integration tests and owns the run mechanics / output shape
- [R6] Martin Fowler, *IntegrationTest* (narrow vs broad; the ambiguity; the seam): <https://martinfowler.com/bliki/IntegrationTest.html>
- [R7] Ham Vocke, *The Practical Test Pyramid* (treat integration narrowly, one integration point at a time): <https://martinfowler.com/articles/practical-test-pyramid.html>
- [R8] Thoughtworks Technology Radar, *Broad integration tests* (hold): <https://www.thoughtworks.com/radar/techniques/broad-integration-tests>
- [R9] Thoughtworks Technology Radar, *Enterprise-wide integration test environments* (hold): <https://www.thoughtworks.com/radar/techniques/enterprise-wide-integration-test-environments>
- [R10] Martin Fowler, *ContractTest* (doubles return the same results as the real service): <https://martinfowler.com/bliki/ContractTest.html>
- [R11] Testcontainers, *Replace H2 with a real database for testing* (real disposable containers; dialect drift in in-memory fakes): <https://testcontainers.com/guides/replace-h2-with-real-database-for-testing/>
- [R12] Google Testing Blog, *Where do our flaky tests come from?* (larger tests are more flake-prone): <https://testing.googleblog.com/2017/04/where-do-our-flaky-tests-come-from.html>
- [R13] `spec/project/test-falsifiability/`: the cross-tier taxonomy of tests that can't fail; `T9` is the failure mode a doubled neighbour more permissive than what it replaces produces, and the spec carries the review question that detects it

## Open Questions

- Should the portfolio require Testcontainers-style ephemeral real dependencies as the default for the datastore seam, or permit a documented in-memory fake where the team accepts the fidelity trade-off?
- Which narrow integration tests are fast enough to gate a PR versus belong in a nightly stage—should the spec set an order-of-magnitude budget, or leave the split per-project?
- Does the integration tier's develop/execute/analyse triad need a dedicated integration-test author agent, or does it share an author capability with the component tier (both wire a harness and doubles)?
- ~~When a seam is a service the project owns but deploys separately, is its verification an integration test (real owned collaborator) or a contract test (cross-service agreement)—and should the spec give a decision rule beyond "own and control"?~~ **Settled (2026-07-24): the release boundary decides, and yes, the spec states the rule.** Integration when the team deploys *and* versions both sides in lockstep; contract as soon as either side can ship independently, even under one owner. "Own and control" was the wrong discriminator because it answers a question about org chart, while the failure the tier must catch is version skew across a release boundary the two sides don't share—which independent deployability creates and common ownership doesn't remove. The rule is recorded in §"Purpose and scope boundary" above, and `spec/project/test-tier-contract/` [R3] is aligned so its "fully owns" exclusion now reads "owns and releases in lockstep," closing the gap where both specs claimed the same common case.
