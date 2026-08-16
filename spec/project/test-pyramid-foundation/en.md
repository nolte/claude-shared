# Test Pyramid Foundation

Status: draft

## Context

Every project in the portfolio needs an automated test suite, but "write tests" isn't a strategy. Without a shared model, suites drift into the two classic failure modes: a thin base with a bloated top (the *ice-cream-cone* anti-pattern—slow, flaky end-to-end tests standing in for cheap checks), or an incoherent pile where nobody can say which behaviour is verified at which level. The reusable, portfolio-wide part of testing isn't any particular test or tool—it's the **model that decides what to test at which level, how the levels compose, and which invariants every level must hold**. That model is framework- and language-independent. The throwaway part is the per-tier glue: which runner, which assertion library, which directory.

This spec is the **foundation** of the portfolio's test-automation discipline. It owns the tier model, the closed functional-tier taxonomy, the orthogonal cross-cutting (non-functional) dimensions, and the governance invariants that hold across every tier. It's deliberately the *apex* document: it doesn't exhaustively specify how to write a unit test or an integration test—instead it defines the **invariant shape every per-tier spec must fill**, so that the per-tier specs written on top of it stay mutually consistent, non-overlapping, and discoverable. The end state is a small family: this foundation, one spec per functional tier, optionally one spec per cross-cutting dimension, and a layer of skills and agents that develop, execute, and analyse tests at each tier.

The model is grounded in the established literature rather than invented: the Test Pyramid (Cohn, popularised and refined by Fowler [R5], [R6]), its practical restatement (Vocke [R7]), the explicit warning that the shape debate is meaningless without shared definitions of "unit" and "integration" (Fowler, *On the Diverse And Fantastical Shapes of Testing* [R8]), the architecture-specific counter-models (Dodds' Testing Trophy for frontend [R9], Spotify's Testing Honeycomb for microservices [R10]), the test-double vocabulary (Meszaros via Fowler [R11]), consumer-driven contract testing as the microservice replacement for broad integration (Fowler [R12], Pact [R13], Thoughtworks "hold" on broad integration tests [R14]), and the governance evidence on flakiness (Google [R15]), coverage-as-a-vanity-metric (Fowler [R16], Google [R17]), and mutation testing as the stronger signal (pitest [R18]).

**Relationship to the existing test specs.** Three test specs already exist and stay authoritative for their tier or function; this foundation references them as tier realisations rather than restating them:

- `spec/project/e2e-test-automation/`: the E2E-tier realisation (page-object discipline, condition-based waits, screenshot/protocol auditability, the Selenium + pytest reference profile, the `test-pyramid-check` skill, and the three `e2e-*` agents). Its embedded §"Test-tier completeness (the pyramid)" subsection predates this foundation; that tier model is **migrated here** and the e2e spec will be reduced to reference this foundation in a follow-up (see Open Questions).
- `spec/project/test-case-derivation/`: derives the abstract, framework-agnostic test cases (TC-IDs) that the per-tier suites automate; the `test-case-extractor` agent realises it. This foundation owns the traceability contract those TC-IDs flow through, not the derivation technique.
- `spec/project/quality-gate/`: executes the fast tiers (lint + typecheck + test) as a single invocation and classifies pass/fail; the `quality-gate` skill realises it. This foundation owns the *CI-gating model* (which tiers gate a PR); quality-gate owns the *execution and output shape* of the fast tiers.

Readers: spec authors writing the per-tier specs on top of this foundation; skill and agent authors building the per-tier test-development/execution/analysis tooling; QA engineers and developers deciding at which tier a behaviour belongs; reviewers checking that a suite is tier-balanced, deterministic, traceable, and gated.

## Goals

- Own the **tier model** once, framework-neutrally: the anchor Test Pyramid plus the documented architecture-specific variants, so each project picks a shape on evidence rather than dogma
- Define a **closed functional-tier taxonomy** (static analysis → unit → component → integration → contract → end-to-end) that every per-tier spec slots into without overlap or gap
- Define the **per-tier invariant shape** (the meta-contract that every per-tier spec must fill) so the derived specs stay structurally consistent and reviewable against a single template
- Treat **cross-cutting / non-functional** concerns (performance, accessibility, security, mutation, visual regression, exploratory) as orthogonal layers applied *at* tiers, never as another pyramid level
- Encode the **governance invariants** that hold across all tiers: determinism over flakiness, lowest-level-that-gives-confidence over fixed ratios, coverage-as-guide-not-target, mutation score as the stronger signal, requirement→case→test traceability, and a staged CI-gating model
- Stay **tool-agnostic**: name tools only as illustrative examples and let each per-tier spec pin its own optional reference profile, exactly as `e2e-test-automation` pins Selenium + pytest
- Provide the **roadmap** under which the per-tier specs, cross-cutting specs, and per-tier skills/agents are written

## Non-Goals

- Exhaustively specifying how to author a test at any one tier—each functional tier gets (or already has) its **own** spec built on this foundation's invariant shape; this document defines the shape, not the per-tier detail
- Restating the E2E discipline, the test-case-derivation technique, or the quality-gate execution contract—those remain owned by `spec/project/e2e-test-automation/`, `spec/project/test-case-derivation/`, and `spec/project/quality-gate/` respectively
- Mandating a specific runner, assertion library, mocking framework, or automation tool for any tier—tool names in this spec are illustrative; binding tool choices, if any, live in a per-tier spec's optional reference profile
- Prescribing a **fixed numeric distribution** of tests across tiers (for example, "70-20-10"); fixed ratios are an anti-pattern per [R5], [R7], [R8] and this spec forbids encoding them as a requirement
- Authoring or editing the requirement documents that test cases trace back to
- Building the skills and agents themselves—this spec declares the roles and their tier mapping; the artefacts are authored separately via `skill-management` / the plugin-developer flow and governed by `spec/claude/`
- Picking the per-project test-tier balance—the *shape decision* is per-project and evidence-driven; this spec gives the decision rule, not the answer

## Requirements

### The tier model and its variants

- **MUST** adopt the **Test Pyramid as the portfolio's anchor model**: a suite is structured as layers where lower layers are more numerous, faster, cheaper, and more isolated, and higher layers are fewer, slower, costlier, and broader in scope, on the inverted cost/speed/brittleness basis described by [R5], [R6].
- **MUST** treat the pyramid as a **decision heuristic, not a quota**: the governing rule is *"write the test at the lowest tier that still gives you the confidence you need"* [R5], [R7]. A higher-tier test is justified only when no lower-tier test can establish the same confidence.
- **MUST NOT** encode a fixed cross-tier ratio (such as 70-20-10) as a normative requirement in this or any derived spec; fixed distributions are explicitly an anti-pattern [R7], [R8].
- **MUST** recognise that the shape debate is incoherent without shared tier definitions—"unit" and "integration" are used inconsistently across teams [R8]—and therefore **MUST** bind to this spec's §"Functional tier taxonomy" definitions whenever a tier name is used in a derived spec, skill, or agent.
- **SHOULD** document the recognised **architecture-specific variants** and when each fits, without treating any as a competitor to the anchor:
  - *Testing Trophy* (Dodds [R9])—static → unit → integration → E2E with the **integration tier the largest**, justified by "the more your tests resemble the way your software is used, the more confidence they give"; fits **frontend / UI-heavy** code.
  - *Testing Honeycomb* (Spotify [R10])—a small core of isolated tests, a **large integrated-test middle**, few implementation-detail tests; fits **microservices**, where most complexity is *between* services and a classic pyramid can be actively misleading.
  - *Ice-cream cone*: pyramid inverted (many manual/E2E, few unit); named explicitly as an **anti-pattern** to detect and correct.
  - *Testing Diamond*: a fat integration middle with thin unit and E2E ends; a recognised shape for integration-dominant systems.
- **MUST** let each consuming project **choose its shape per evidence** (architecture, change-failure data, flake rate) and record that choice; the choice is a per-project decision, not a portfolio mandate.

### Functional tier taxonomy

- **MUST** treat the following as the **closed, ordered set** of functional tiers, from foundation to apex. Every per-tier spec, skill, and agent maps to exactly one entry; a behaviour is tested at the lowest applicable entry:
  1. **Static analysis**: lint, type-check, format-check, and static security/complexity rules. Executes without running the program; the pyramid's foundation layer per the Trophy [R9]. Owned in execution by `spec/project/quality-gate/`.
  2. **Unit**: verifies one unit of behaviour in isolation. **Solitary** unit tests isolate the unit from collaborators with test doubles; **sociable** unit tests exercise real collaborators [R6], [R11]. The definition of "a unit" is **deliberately team-determined** [R6] and a per-project unit spec records it.
  3. **Component**: verifies a single deployable/shippable component in isolation from its peers: a rendered frontend component against its own contract, or a backend service exercised through its own interface with its external dependencies replaced by doubles at the process boundary.
  4. **Integration**: verifies that a unit/component correctly talks to an adjacent real collaborator. **Narrow integration** exercises one real collaborator (for example, a database via an ephemeral container) with the rest doubled; **broad integration** stands up many live services and **MUST** be treated as costly and minimised [R12], [R14].
  5. **Contract**: verifies the agreement at a service boundary without standing up both sides. **Consumer-driven contracts** [R12], [R13] let a consumer's expectations be verified against a provider independently; in microservice architectures contract tests **SHOULD** replace broad integration tests across service boundaries [R13], [R14].
  6. **End-to-end / system**: drives the real user-facing surface of a running system and asserts on observable behaviour. Few, slow, and the most flake-prone; governed in full by `spec/project/e2e-test-automation/`.
- **MUST NOT** introduce a new functional tier in a derived spec without amending this taxonomy first; the closed set prevents the murky-definitions problem [R8].
- **MAY** omit any tier that doesn't apply to a given project (for example, no contract tier when the system exposes and consumes no service boundary), recorded as a deliberate, justified omission rather than a silent gap.

### Per-tier invariant shape (the meta-contract)

- Every **per-tier spec MUST** define, at minimum, the following so the family stays structurally consistent and reviewable against one template:
  - **Purpose & scope boundary**: what this tier verifies and, explicitly, what it **MUST NOT** assert (the boundary against the tier below and above).
  - **Isolation level & permitted test doubles**: which collaborators are real and which are doubled, using the §"Test-double taxonomy" vocabulary.
  - **Speed & determinism budget**: an order-of-magnitude expectation (for example, milliseconds for unit, seconds for integration) and the determinism guarantee the §"Determinism and flakiness" section requires.
  - **Execution placement**: pre-commit / PR-gating CI / nightly, consistent with the "CI gating model" section.
  - **Traceability**: how a test at this tier names the requirement / TC-ID it verifies, as the §"Traceability" section requires.
  - **Canonical anti-patterns**: the tier-specific smells a reviewer rejects (for example, fixed `sleep` in E2E, raw collaborator access in solitary unit tests, asserting implementation detail in integration).
  - **Optional reference profile**: a fully worked, stack-specific default **MAY** be pinned (as `e2e-test-automation` pins Selenium + pytest), clearly demoted to "reference," never elevated to a requirement.
- A per-tier spec **MUST** declare its boundaries against its neighbouring tiers by responsibility, so two tier specs never claim the same behaviour.

### Test-double taxonomy

- **MUST** use the five **Meszaros test-double categories** [R11] with these meanings, portfolio-wide, so tier specs and reviews speak one vocabulary:
  - **Dummy**: passed to fill a parameter list, never actually used.
  - **Fake**: a working but shortcut implementation unsuitable for production (for example, an in-memory repository).
  - **Stub**: supplies canned answers to calls made during the test; supports **state verification**.
  - **Spy**: a stub that also records how it was called.
  - **Mock**: pre-programmed with expectations and used for **behaviour verification** (asserting *how* collaborators were called) [R11].
- **MUST** distinguish **state verification** (assert the resulting state) from **behaviour verification** (assert the interactions); a tier spec states which it expects, and over-using behaviour verification (over-mocking) **MUST** be flagged as the smell that couples tests to implementation.
- **MUST NOT** let a double be **more permissive than the collaborator it replaces** along any dimension the test relies on: it rejects what the real collaborator rejects (constraints, validation, uniqueness) and doesn't preserve what the real collaborator discards. The rules above bound *how much* a test doubles; this one bounds whether the double can **refuse**. A double that accepts what production rejects makes a correct, specific, falsifiable assertion certify a state that can't occur, so the test passes for a world that doesn't exist—the failure mode catalogued as `T9` by `spec/project/test-falsifiability/` [R20], which owns its detection route while this rule owns the requirement.
- **MUST** name the divergence **in the double itself** where a double can't be made faithful, so the next reader knows what the test doesn't cover. An unfaithful double whose divergence is declared is a bounded trade-off a reviewer can weigh; an unfaithful double whose divergence is silent is the defect, and this asymmetry is what makes the rule above checkable rather than aspirational.
- **MUST** let each per-tier spec express this rule for its own doubling practice—the seams it doubles, and the constraints most often dropped there—without restating it, per the invariant shape's *Isolation level & permitted test doubles* field.

### Cross-cutting (non-functional) dimensions

- **MUST** treat the following as **orthogonal dimensions applied at one or more functional tiers**, never as an additional pyramid layer:
  - **Performance / load**: applied at component, integration, or E2E scope; gates a release, not usually a PR.
  - **Accessibility (a11y)**: applied at component and E2E scope (for example, automated rule checks on rendered output).
  - **Security**: **SAST** (static analysis of source) sits at the static-analysis tier; **DAST** (dynamic analysis of a running system) sits at the E2E/system scope [R19]. The boundary against `spec/project/dependency-audit/` (dependency CVEs) is preserved.
  - **Mutation testing**: a **meta-measure of suite quality**, not a tier: it mutates production code and checks the suite catches the change, giving a stronger signal than coverage [R18]. Reported as a suite-quality metric, as the §"Coverage and suite-quality metrics" section requires.
  - **Visual regression**: applied at component and E2E scope; compares rendered output against a baseline.
  - **Exploratory / manual**: unautomated, human, complementary to the automated tiers; recorded but never gating.
- A cross-cutting dimension **MAY** earn its own spec under this foundation, but **MUST** state which functional tiers it attaches to rather than redefining a tier.

### Determinism and flakiness

- **MUST** require every automated test to be **deterministic**: same input ⇒ same result, independent of execution order, wall-clock time, network weather, or concurrent runs.
- **MUST** treat a **flaky test** (one that passes and fails without a code change) as a defect in its own right: flakiness erodes trust in the whole suite [R15]. A flaky test **MUST** be quarantined (excluded from the gating signal, tracked as a defect) rather than left to fail intermittently or be silently re-run forever.
- **MUST NOT** use fixed time delays (`sleep`) to synchronise; waits are condition-based (the E2E realisation of this is in `spec/project/e2e-test-automation/`).
- **SHOULD** make tests independent and self-contained—each sets up and tears down its own state—so they can run in any order and in parallel.

### Test data and isolation

- **MUST** isolate test data per test so that no test depends on the residue of another; shared mutable fixtures across tests are forbidden.
- **SHOULD** prefer ephemeral, programmatically seeded data (for example, per-test factories, ephemeral containers at the integration tier) over shared long-lived fixtures.
- **MUST** scope external real resources (databases, message brokers) to the narrow-integration tier and tear them down deterministically.

### Coverage and suite-quality metrics

- **MUST** treat line/branch **coverage as a guide, not a target**: driving coverage to a fixed number invites Goodhart's law and produces assertion-free tests that exercise code without verifying it [R16], [R17].
- **MUST NOT** gate a PR solely on a coverage percentage threshold as the primary quality signal; coverage gaps prompt the question "is this risk worth a test?" and never an automatic fail [R16].
- **SHOULD** use **mutation score** as the stronger suite-quality signal where the toolchain supports it, since it measures whether tests actually catch behavioural changes rather than merely execute lines [R18].
- **MAY** report coverage as an informational trend; it's observed, not chased.

### CI gating model

- **MUST** stage execution by tier so feedback is fast: the **fast tiers** (static analysis, unit, component, narrow integration, contract) **MUST** gate a pull request, mirroring `spec/project/quality-gate/` for the lint/typecheck/test subset.
- **SHOULD** run the **slow or broad tiers** (E2E, broad integration, performance, full DAST) on a schedule (nightly) or a dedicated stage rather than blocking every PR, unless a project's risk profile justifies gating on them.
- **MUST** keep the **required-status-check** set for the integration branch declared as code per `spec/project/pull-request-workflow/`: this spec defines *which tiers belong in the gate*, that spec defines *how the gate is enforced*.
- **MUST** route a failing required test tier to fix-forward / `workflow-health` triage, never to a waiver, consistent with the quality-gate and pull-request-workflow specs.

### Traceability

- **MUST** preserve an unbroken chain **requirement → abstract test case (TC-ID) → automated test** across tiers: a test names the TC-ID (and through it the requirement) it verifies, so coverage of *requirements*, not just code, is auditable.
- **MUST** consume the abstract cases produced under `spec/project/test-case-derivation/` (their TC-IDs) rather than re-deriving them; this spec owns the chain, not the derivation.
- **SHOULD** make the TC-ID visible in the test itself (name, tag, or docstring) so a run's report maps back to requirements without external bookkeeping.

### Test authoring conventions

- **MUST** structure each test as **Arrange–Act–Assert** (equivalently Given–When–Then): set up state, exercise one behaviour, assert the observable outcome.
- **MUST** give each test an **intention-revealing name** that states the behaviour and expected outcome, not the method under test.
- **MUST** keep tests **independent** (no ordering dependency, no shared mutable state), as the §"Determinism and flakiness" section requires.
- **SHOULD** assert on **observable behaviour** rather than implementation detail, so a refactor that preserves behaviour doesn't break the test (strongest at higher tiers, balanced against isolation at lower tiers).

### Tool-agnosticism and derived artefacts

- **MUST** keep this foundation and every per-tier spec **tool-agnostic** in their binding requirements; tool names (pytest / JUnit / Vitest at unit; Testcontainers at integration; Pact at contract; Playwright / Selenium / Cypress at E2E; pitest / mutmut / Stryker for mutation; k6 / Gatling / Locust for performance; axe for a11y) appear only as illustrative examples.
- **MUST** plan the operationalisation as a **per-tier role triad** of *develop* (scaffold/author tests for the tier), *execute* (run and collect results), and *analyse* (review results / suite quality), realised by skills and agents authored under `spec/claude/`. The existing E2E artefacts (`e2e-test-generator`, `e2e-test-reviewer`, `e2e-result-reviewer`, `test-pyramid-check`) are the **template** for this triad at the E2E tier; derived tiers follow the same develop/execute/analyse shape.
- **MUST** declare, when a derived skill or agent is created, which functional tier (or cross-cutting dimension) and which triad role it occupies, so the portfolio map stays gap- and overlap-free.
- **MUST** bind the `test-pyramid-check` skill's **tier-completeness** audit to **this foundation**: it audits, per feature, which of the closed functional tiers are present, which are missing, and which are `n/a` with a reason, against the taxonomy and the lowest-tier-that-gives-confidence rule defined here. The skill's **E2E-discipline** audit stays bound to `spec/project/e2e-test-automation/` [R1], which owns that tier's shape. The skill therefore has two binding targets, one per axis, and neither spec restates the other's half.

## Acceptance Criteria

- [ ] The spec defines the Test Pyramid as the anchor model and documents the Trophy, Honeycomb, ice-cream-cone, and diamond variants with their architecture fit, each cited to a primary source
- [ ] The spec states the lowest-tier-that-gives-confidence rule and explicitly forbids encoding a fixed cross-tier ratio as a requirement
- [ ] The functional-tier taxonomy is a closed, ordered list of exactly six tiers (static analysis, unit, component, integration, contract, end-to-end), each with a one-line scope and an owning or to-be-created spec
- [ ] The per-tier invariant shape enumerates every field a derived per-tier spec must fill (purpose/boundary, isolation/doubles, speed/determinism, placement, traceability, anti-patterns, optional reference profile)
- [ ] The five Meszaros test-double categories are defined with the state-vs-behaviour-verification distinction
- [ ] Double fidelity is required portfolio-wide (a double never more permissive than what it replaces), an undeclared divergence is forbidden while a declared one is permitted, and per-tier expression is delegated to the tier specs
- [ ] Cross-cutting dimensions (performance, a11y, security SAST/DAST, mutation, visual regression, exploratory) are defined as orthogonal layers that name the tiers they attach to, never as a pyramid level
- [ ] Determinism is required, flakiness is defined as a defect with a quarantine rule, and fixed `sleep` synchronisation is forbidden
- [ ] Coverage is bound as a guide-not-target with the Goodhart caveat, and mutation score is named as the stronger suite-quality signal
- [ ] The CI-gating model assigns fast tiers to PR gating and slow/broad tiers to scheduled runs, and defers gate *enforcement* to `spec/project/pull-request-workflow/`
- [ ] The traceability chain requirement→TC-ID→test is required, consuming `test-case-derivation` output rather than re-deriving it
- [ ] The relationship section maps the three existing test specs as tier/function realisations without restating them, and records the migration of the e2e "pyramid" subsection into this foundation as a follow-up
- [ ] The derived-artefacts section declares the develop/execute/analyse triad, names the existing E2E artefacts as its template, and binds `test-pyramid-check`'s tier-completeness axis to this foundation while its E2E-discipline axis stays bound to `e2e-test-automation`
- [ ] EN and DE versions are structurally identical (same headings, requirement count, and acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/e2e-test-automation/`: End-to-End Test Automation Standard (the E2E-tier realisation; source of the migrated pyramid subsection)
- [R2] `spec/project/test-case-derivation/`: Test-Case Derivation from Requirements (produces the TC-IDs this foundation's traceability chain consumes)
- [R3] `spec/project/quality-gate/`: Quality Gate (executes the fast tiers; owns gate output shape)
- [R4] `spec/project/pull-request-workflow/`: owns required-status-check enforcement that this spec's CI-gating model feeds
- [R5] Martin Fowler, *TestPyramid*: <https://martinfowler.com/bliki/TestPyramid.html>
- [R6] Martin Fowler, *UnitTest* (solitary vs sociable; team-determined unit): <https://martinfowler.com/bliki/UnitTest.html>
- [R7] Ham Vocke, *The Practical Test Pyramid*: <https://martinfowler.com/articles/practical-test-pyramid.html>
- [R8] Martin Fowler, *On the Diverse And Fantastical Shapes of Testing*: <https://martinfowler.com/articles/2021-test-shapes.html>
- [R9] Kent C. Dodds, *The Testing Trophy and Testing Classifications*: <https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications>
- [R10] Spotify Engineering, *Testing of Microservices* (Testing Honeycomb): <https://engineering.atspotify.com/2018/01/testing-of-microservices>
- [R11] Martin Fowler, *Mocks Aren't Stubs* (Meszaros test-double taxonomy): <https://martinfowler.com/articles/mocksArentStubs.html>
- [R12] Martin Fowler, *IntegrationTest* / *ContractTest*: <https://martinfowler.com/bliki/IntegrationTest.html> , <https://martinfowler.com/bliki/ContractTest.html>
- [R13] Pact—consumer-driven contract testing: <https://docs.pact.io/>
- [R14] Thoughtworks Technology Radar, *Broad integration tests* (hold): <https://www.thoughtworks.com/radar/techniques/broad-integration-tests>
- [R15] Google Testing Blog, *Flaky Tests at Google and How We Mitigate Them*: <https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html>
- [R16] Martin Fowler, *TestCoverage*: <https://martinfowler.com/bliki/TestCoverage.html>
- [R17] Google Testing Blog, *Code Coverage Best Practices*: <https://testing.googleblog.com/2020/08/code-coverage-best-practices.html>
- [R18] pitest—mutation testing: <https://pitest.org/>
- [R19] SAST vs DAST (security testing placement): <https://blog.jetbrains.com/teamcity/2025/05/sast-vs-dast/>
- [R20] `spec/project/test-falsifiability/`: the cross-tier taxonomy of tests that can't fail; consumes this spec's mutation-score guidance and forbids counting non-falsifiable tests as tier coverage

## Open Questions

- Should the functional-tier specs be created one-per-tier (six specs) or grouped (for example, a single "fast tiers" spec covering static/unit/component and a "boundary tiers" spec covering integration/contract)? The granularity affects how many derived skills/agents the triad produces.
- ~~When the e2e spec's embedded §"Test-tier completeness (the pyramid)" subsection is reduced to a reference to this foundation, does `test-pyramid-check` retarget to this spec, or stay pointed at the e2e spec for E2E-tier discipline only?~~ **Settled (2026-07-24): both, split by axis.** Tier completeness retargets here; E2E discipline stays on `e2e-test-automation` [R1]. This is what the shipped skill already does—its frontmatter and its read step name both specs, and its conflict rule names each as the authority for its own half—so the decision ratifies the real wiring instead of inventing a target. The alternative single-target readings both break something: pointing wholly at the e2e spec would leave a UI-less project's tier audit governed by an E2E spec, while pointing wholly here would orphan the E2E-discipline checks the foundation deliberately doesn't own. The mandate at §"Tool-agnosticism and derived artefacts" above and the corresponding requirement in the e2e spec are migrated to match, so the skill's two axes each have exactly one owner.
- Do the cross-cutting dimensions (performance, a11y, security, mutation, visual regression) each warrant their own spec, or a single "non-functional testing" spec that enumerates them? Several already have partial homes (security overlaps `dependency-audit`; a11y overlaps `webview-ui-optimization`).
- Should a per-project "test strategy record" (the chosen shape + justified tier omissions) be a required artefact (for example, under `project/`) or an optional note?
