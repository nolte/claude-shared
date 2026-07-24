# Test Tier: Contract

Status: draft

## Context

The contract tier verifies a **service-to-service agreement at a boundary without standing up both sides live**. It's the apex of the pyramid's functional tiers defined by `spec/project/test-pyramid-foundation/`, and it exists to solve a specific problem the other tiers can't: when one service consumes another, the consumer's tests use a **double** of the provider, and that double silently **drifts** from what the real provider actually returns. A contract test closes that gap—it checks that the doubles a consumer relies on return the **same results the real provider would** [R5], [R6], so a breaking change on either side is caught at the boundary rather than in production.

In a **consumer-driven** contract (the reference model), the **consumer** records its expectations of the provider as a contract; the **provider** is then verified independently against that contract. Neither service needs the other running at the same time: the consumer runs against a mock that emits the contract, and the provider replays the contract's recorded interactions against its real implementation. This is why, in a microservice architecture, a contract test **replaces a broad integration test across a service boundary** (per the foundation): the agreement is verified without a shared, fragile integration environment.

This spec is the per-tier realisation of the foundation's **invariant shape** for the contract tier. It fills every field that shape mandates and adds the tier-specific substance: the consumer-driven model and its provider-driven and bi-directional variants, the compatibility-of-the-agreement assertion scope, the broker and `can-i-deploy` deployment gate, and the boundary to the integration tier.

It's deliberately **tool-agnostic**: the binding requirements never name a tool. Concrete tools appear only as an illustrative reference profile.

**Relationship to the other specs.** This tier is bounded by responsibility, not by overlap:

- `spec/project/test-pyramid-foundation/` [R1] owns the tier model and the claim that contract tests replace broad integration across service boundaries. This spec details the contract tier; it doesn't restate the model.
- `spec/project/test-tier-integration/` [R2] is the sibling tier for a collaborator the project **owns and exercises live** (its own database, broker, or service) through a real connection. The boundary is "one real owned collaborator, exercised live" (integration) vs "a cross-service agreement verified without either side live" (contract).
- The **unit** and **component** tiers (`spec/project/test-tier-unit/`, `spec/project/test-tier-component/`) verify each service's **own internal correctness**; the contract tier verifies the **cross-boundary agreement** between two services, asserting nothing about either service's internal behaviour [R7].
- `spec/project/e2e-test-automation/` [R8] verifies the whole running system; the contract tier verifies a **single boundary's compatibility**, not an end-to-end journey.
- `spec/project/quality-gate/` [R9] **executes** the consumer-side contract tests in the fast gate and owns the run mechanics and output shape.

Readers: spec authors writing the sibling per-tier specs; skill and agent authors building the contract-tier development/execution/analysis triad; developers writing consumer and provider contract tests across service boundaries; reviewers checking that a contract test asserts compatibility (not business logic) and is wired to a broker with a deployment gate.

## Goals

- Define the contract tier as verification of a service-boundary agreement **without both sides live**, closing the stub-drift gap
- Establish the **consumer-driven** model as the reference and document the provider-driven and bi-directional variants with their fit
- Scope assertions to the **compatibility of the agreement** (message shape, field presence and types, status codes, the protocol-level interaction), never business logic or end-to-end behaviour
- Require a **contract exchange (broker)** and a **`can-i-deploy`-style compatibility gate** before deployment, so a contract that isn't verified against the current provider can't ship
- Draw a crisp boundary to the integration tier (a real owned collaborator released in lockstep and exercised live) and to E2E (the whole system)
- Keep the tier tool-agnostic, with a swappable reference profile rather than a mandated framework

## Non-Goals

- Executing the tier or defining its run mechanics and output table: owned by `spec/project/quality-gate/` [R9]
- Exercising a **real owned collaborator released in lockstep** live (a real database or broker over a connection, or an owned service deployed and versioned together with the code under test): that's the integration tier [R2]
- Verifying either service's **business logic or internal correctness**: that's each service's own unit and component tiers [R7]
- Driving a **whole-system journey**: that's the E2E tier [R8]
- Standing up **both** the consumer and the provider together: the contract tier exists precisely to avoid that
- Mandating a specific contract framework, broker, or schema format: the reference profile is illustrative

## Requirements

### Purpose and scope boundary

- **MUST** define a contract test as one that verifies a component meets a **contract another component expects of it**, ensuring the **doubles a consumer uses return the same results the real provider would**: without standing up both services live [R5], [R6].
- **MUST** keep the boundary to the **integration tier** sharp: integration exercises a real collaborator the project owns and controls, **live** through a real connection; the contract tier verifies a **cross-service agreement** with neither side stood up live [R2], [R6].
- **MUST** keep the boundary to the **unit and component tiers** sharp: those verify a service's own internal correctness; a contract test asserts only the **cross-boundary agreement** and nothing about either service's internal behaviour [R7].
- **MUST** keep the boundary to **E2E** sharp: a contract test verifies a single boundary's compatibility, not the whole system end to end [R8].

### Consumer-driven contracts (the reference model)

- **MUST** adopt **consumer-driven contracts** as the reference model: the **consumer** defines its expectations of the provider as the contract (typically the subset of the provider's surface the consumer actually uses), and the **provider** is **verified independently** against that contract [R6], [R10], [R11].
- **MUST** verify the provider by **replaying the contract's recorded interactions against the real provider implementation** (provider verification), with a provider-state / setup mechanism to put the provider into the precondition each interaction needs [R12].
- **MUST** treat the consumer-side run as executing against a **mock that emits the contract**, so the consumer test is fast, deterministic, and needs no live provider [R12], [R14].

### The three flavours

- **MUST** recognise the three flavours and let a project pick the one matching its constraints:
  - **Consumer-driven** (reference): consumer expectations drive the contract; the provider is verified against it. Best when consumer and provider evolve independently and both sides can run the framework [R6], [R11].
  - **Provider-driven**: the provider publishes the contract and consumers receive generated stubs from it; the producer owns the contract definition. Useful when one provider serves many consumers and owns the API shape [R13].
  - **Bi-directional**: the provider publishes a static API specification (for example OpenAPI) and the consumer's mock/contract is verified against that spec, with **no execution of provider code**: a more decoupled approach when running provider verification is impractical [R15].
- **SHOULD** default to the **consumer-driven** flavour and record a justification when choosing provider-driven or bi-directional, because consumer-driven catches the consumer-relevant breaking changes most directly.

### What a contract test verifies, and what it must not

- **MUST** scope assertions to the **compatibility of the agreement**: the request/response structure, field presence and types, status codes, and the protocol-level interaction at the boundary [R5], [R7].
- **MUST NOT** assert **business logic or functional correctness** of either service; that duplicates the services' own unit/component tiers and over-couples the contract [R7].
- **MUST NOT** **over-specify** the contract by asserting on fields or behaviours the consumer doesn't actually use: over-specification creates false breakages when the provider changes something irrelevant to this consumer [R6], [R11].

### Isolation and determinism

- **MUST** keep the tier **fast and deterministic** by standing up **neither real service live**: the consumer runs against a contract mock and the provider replays recorded interactions, so there's no network flakiness, per the foundation's determinism rule [R12].

### The broker and the deployment gate

- **MUST** exchange contracts through a **broker** (a contract repository that versions contracts and verification results and records which consumer and provider versions are compatible) rather than by ad-hoc file sharing [R16].
- **MUST** gate deployment with a **`can-i-deploy`-style compatibility check**: before a consumer or provider version is deployed, the broker is queried to confirm that version is verified-compatible with the versions it will meet in the target environment [R17].
- **MUST NOT** allow **contract drift**: a contract that isn't verified against the current provider (no broker, no `can-i-deploy`) gives false confidence and is a spec violation [R16], [R17].

### Execution placement

- **MUST** run the **consumer-side** contract test in the **consumer's pipeline** as a fast PR-gating check (executed per `spec/project/quality-gate/`, declared required per `spec/project/pull-request-workflow/`).
- **MUST** run **provider verification** in the **provider's pipeline** against published consumer contracts, and run the **`can-i-deploy` gate** as a pre-deployment check, so neither side ships a breaking change.

### When to use, when not

- **MUST** apply the contract tier at **service-to-service / API boundaries** where consumer and provider evolve independently and breaking changes must be caught **without a shared integration environment**: the foundation's microservice case where contract tests replace broad integration [R1].
- **MUST NOT** apply it to a boundary the project **owns and releases in lockstep with**, already exercised as a narrow integration test (a real database it controls, or an owned service deployed and versioned together with its consumer), nor use it for full functional verification; those are the integration and unit/component tiers respectively [R2], [R7].
- **MUST** apply it, conversely, to a service the project **owns but releases independently**: common ownership doesn't remove the version skew that independent deployment creates, so an owned-but-independently-shipped boundary is a contract boundary. `spec/project/test-tier-integration/` [R2] states the same rule from the other side; the discriminator is the **release boundary**, not ownership.

### Anti-patterns

- **MUST** reject, as canonical anti-patterns: testing business logic in contracts; treating contract tests as full functional or integration tests; contract drift (no broker, no `can-i-deploy`); over-specifying the contract beyond what the consumer uses; and consumer and provider versions that are never reconciled through the broker.

### Traceability

- **MUST** let a contract test that verifies a derived test case name the **TC-ID** (and through it the requirement) it covers, per the foundation's traceability chain, so requirement coverage is auditable.

### Optional reference profile

- **MAY** pin a fully worked, stack-specific reference profile, clearly demoted to "reference." An illustrative consumer-driven profile: a Pact consumer test generating a pact file, provider verification replaying it against the real provider with provider states, and a Pact Broker (or PactFlow) holding the contracts with a `can-i-deploy` deployment gate; Pact exists for the major ecosystems (pact-jvm, pact-python, pact-js, pact-go). For the provider-driven flavour, an illustrative profile is Spring Cloud Contract; for bi-directional, an OpenAPI spec verified against the consumer's mock. Tool names are illustrative, never required.

## Acceptance Criteria

- [ ] The spec defines a contract test as verifying a boundary agreement without both sides live, framed as closing the stub-drift gap, cited to Fowler/Pact
- [ ] The consumer-driven model is established as the reference (consumer defines expectations, provider verified independently by replay), with the provider-state mechanism
- [ ] The three flavours (consumer-driven, provider-driven, bi-directional) are described with their fit, and consumer-driven is the recorded default
- [ ] Assertions are scoped to agreement compatibility (shape, fields, types, status codes, protocol), forbidden from business logic, and the over-specification anti-pattern is named
- [ ] Determinism via neither-side-live (consumer mock + provider replay) is required
- [ ] A broker and a `can-i-deploy`-style deployment gate are required, and contract drift (no broker / no gate) is forbidden
- [ ] Execution placement assigns consumer tests to the consumer pipeline (PR gate), provider verification to the provider pipeline, and can-i-deploy as a pre-deploy gate
- [ ] The when-to-use / when-not rules tie to the microservice case (replace broad integration), exclude lockstep-released owned-collaborator integration and full functional verification, and include an owned-but-independently-released service via the release-boundary discriminator
- [ ] The boundary against the integration tier (real owned collaborator live), the unit/component tiers (internal correctness), and E2E (whole system) is explicit
- [ ] Traceability to TC-ID is required, and an optional clearly-demoted reference profile (consumer-driven + variants) is provided without mandating a framework
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-pyramid-foundation/`: the tier model and the claim that contract tests replace broad integration across service boundaries
- [R2] `spec/project/test-tier-integration/`: the sibling tier (a real owned collaborator exercised live); the integration↔contract boundary
- [R7] `spec/project/test-tier-unit/` and `spec/project/test-tier-component/`: each service's own internal correctness, distinct from the cross-boundary agreement
- [R8] `spec/project/e2e-test-automation/`: the whole-system tier; the contract↔E2E boundary
- [R9] `spec/project/quality-gate/`: executes the consumer-side contract tests and owns the run mechanics / output shape
- [R5] Martin Fowler, *ContractTest* (a component meets a contract another expects; doubles return real-service results): <https://martinfowler.com/bliki/ContractTest.html>
- [R6] Martin Fowler / I. Robinson, *Consumer-Driven Contracts*: <https://martinfowler.com/articles/consumerDrivenContracts.html>
- [R10] M. Fowler & T. Clemson, *Testing Strategies in a Microservice Architecture* (contract tests, not component tests): <https://martinfowler.com/articles/microservice-testing/>
- [R11] Ham Vocke, *The Practical Test Pyramid* (CDC; the consumer-used subset): <https://martinfowler.com/articles/practical-test-pyramid.html>
- [R12] Pact, *How Pact works* / *Provider verification* (consumer mock generates the contract; provider replays it): <https://docs.pact.io/getting_started/how_pact_works> , <https://docs.pact.io/provider>
- [R13] Spring Cloud Contract, *Consumer-Driven Contracts* (provider-driven flavour): <https://docs.spring.io/spring-cloud-contract/reference/getting-started/cdc.html>
- [R14] Microsoft Engineering Playbook, *Consumer-Driven Contract Testing*: <https://microsoft.github.io/code-with-engineering-playbook/automated-testing/cdc-testing/>
- [R15] PactFlow, *Bi-Directional Contract Testing* (provider publishes OpenAPI; no provider code execution): <https://pactflow.io/bi-directional-contract-testing/>
- [R16] Pact, *Pact Broker* (contract exchange, versioning, compatibility matrix): <https://docs.pact.io/pact_broker>
- [R17] Pact, *can-i-deploy* (pre-deployment compatibility gate): <https://docs.pact.io/pact_broker/can_i_deploy>

## Open Questions

- For a portfolio that's mostly a single Claude Code plugin and small services rather than a large microservice estate, is the contract tier typically **omitted as a justified non-applicable tier** (per the foundation's tier-omission rule), and should this spec say so explicitly?
- Should the portfolio standardise on one contract framework and one broker (so `can-i-deploy` gates are uniform across repos), or stay per-project with only the broker + gate requirement?
- Does the contract tier's develop/execute/analyse triad need its own agents, given that it spans two repositories (consumer and provider) and a broker—or is it better operationalised as a cross-repo workflow than as per-repo skills?
- Where a provider serves an external (non-portfolio) consumer, does the bi-directional flavour (publish OpenAPI) become the default, since the external consumer can't run the portfolio's framework?
