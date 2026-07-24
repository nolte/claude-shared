# Test Cycle: Case Determination

Status: draft

## Context

Case determination is **phase 1** of the iterative test cycle owned by `spec/project/test-cycle-foundation/`: deciding *which* test cases are needed and *designing* them, so the next phases have something to execute and analyse. It isn't a one-shot up-front activity—the cycle keeps producing cases: a defect found in analysis becomes a new regression case, a coverage gap surfaces a missing case, exploratory findings get scripted, and a changed requirement retires or adds cases. This spec frames case determination as that recurring **process**.

It's a **process spec that references existing capability specs**, not a restatement of them. `spec/project/test-case-derivation/` already owns the *technique* of deriving abstract, framework-agnostic cases from a requirement document (the `test-case-extractor` agent realises it); this spec consumes that capability and adds the cycle-level concerns: recognising the full family of design techniques, selecting cases by risk, the iterative-feedback rule that the cycle never stops producing cases, and the quality bar a case must meet—while deferring *which tier* a case lands at to the tier model.

This spec fills the foundation's **per-phase meta-contract** (purpose and scope boundary, inputs and outputs, required best practices, referenced capability specs, feedback edges, anti-patterns). It's deliberately tool- and tier-agnostic.

**Relationship to the other specs.** Bounded by responsibility:

- `spec/project/test-cycle-foundation/` [R1] owns the cycle, the loop, and this phase's inter-phase contract. This spec details phase 1.
- `spec/project/test-case-derivation/` [R2] owns the requirement → abstract-case derivation technique; this spec references it for that step and **MUST NOT** restate it.
- `spec/project/test-pyramid-foundation/` [R3] owns the closed tier taxonomy; this spec decides *that* a case is needed and designs it, while *which tier* it lands at is the tier model's call (lowest tier that gives confidence).
- `spec/project/quality-gate/` [R4] and the tier specs own execution; a coverage report from execution feeds *back* into this phase to surface missing cases.

Readers: spec authors writing the sibling phase specs; skill and agent authors building a case-determination capability; developers and testers deciding what to test; reviewers checking that a case set is risk-prioritised, traceable, and not redundant.

## Goals

- Frame case determination as a **recurring process** that runs throughout the cycle, not only up front
- Require recognition of the full **technique families** (specification-based / black-box, structure-based / white-box, experience-based) and the example-driven, property-/model-based, and risk-based methods
- Make the **iterative-feedback** rule binding: the cycle keeps producing cases (regression-for-defect, coverage gap, exploratory finding, requirement change)
- Encode a **case quality bar** (independent, deterministic-by-design, one behaviour, intention-revealing, asserting observable behaviour, non-redundant)
- Reference `test-case-derivation` for requirement-derived cases and defer tier placement to the tier model—no duplication
- Keep the phase tool- and tier-agnostic

## Non-Goals

- Restating the requirement → abstract-case **derivation technique**: owned by `spec/project/test-case-derivation/` [R2]
- Deciding **which tier** a case lands at: owned by `spec/project/test-pyramid-foundation/` [R3] (lowest tier that gives confidence)
- **Executing** the cases or reading their results: phases 2 and 3 of the cycle
- Determining the **code change** that satisfies a case: phase 4 of the cycle
- Mandating a specific test-design tool, BDD framework, or property-based library: methods are named only as illustrative examples

## Requirements

### Purpose and scope boundary

- **MUST** define this phase as **deciding which test cases are needed and designing them**, producing cases that are expected to fail or be absent until satisfied, as phase 1 of the cycle [R1].
- **MUST NOT** restate the requirement → abstract-case derivation technique; where a case derives from a requirement document, this phase **MUST** use `spec/project/test-case-derivation/` [R2] and reference it.
- **MUST** leave **tier placement** to `spec/project/test-pyramid-foundation/` [R3]: this phase determines *that* a case is needed and its design; the tier model fixes *which tier* it lands at.

### Inputs and outputs (the phase-1 contract)

- **MUST** consume, as inputs, any of: requirements / acceptance criteria, **coverage gaps** reported by execution, **defects** classified by result analysis, exploratory findings, and changed behaviour.
- **MUST** produce, as output, a set of test cases each carrying a **TC-ID** and a **chosen tier**, ready for execution (phase 2), per the foundation's inter-phase contract [R1].

### Test-design technique families

- **MUST** recognise the three ISTQB technique families and that case determination draws on all of them [R5]:
  - **Specification-based (black-box)**: design cases from the specification of behaviour without reference to internals.
  - **Structure-based (white-box)**: use code structure (coverage) to find what existing cases miss.
  - **Experience-based**: error guessing and exploratory testing, drawing on tester knowledge of likely defects.
- **MUST** apply the core **black-box techniques** where they fit, each targeting its defect class [R5], [R6]:
  - **Equivalence partitioning**: divide inputs into partitions processed identically; one representative per partition suffices.
  - **Boundary value analysis**: exercise the edges of ordered partitions (2-value and 3-value); targets off-by-one and wrong-relational-operator defects.
  - **Decision-table testing**: derive cases from a condition → outcome table for combinational business rules.
  - **State-transition testing**: derive cases from a state model (`event [guard] / action`); targets invalid or missing transitions.
  - **Use-case testing**: exercise end-to-end scenarios.
  - **Pairwise / combinatorial**: cover all pairs of parameter values when the full combination space is too large.

### Coverage as a guide to missing cases

- **MUST** use **structure-based coverage** (statement, branch/decision, path) as a **guide to surface untested code that needs a new case**, never as a numeric target to chase; coverage-as-a-target is Goodhart's law and produces assertion-free tests, per `spec/project/test-pyramid-foundation/`'s coverage governance and Fowler [R7].

### Example-driven and test-first determination

- **SHOULD** use **Example Mapping** (rules → examples → questions) and **Specification by Example / BDD** (Given-When-Then) to discover concrete examples collaboratively **before** coding, turning acceptance criteria into cases [R8], [R9]; the full, tool-neutral BDD treatment (scenario language, step-definition principles, and the test-case-document-to-scenario derivation) is owned by `spec/project/behavior-driven-development/` [R15].
- **SHOULD** treat **test-first (TDD)** as a case-determination practice: the failing test *is* the case that defines the next increment of behaviour [R1].

### Machine-generated cases

- **MAY** use **property-based testing** (assert invariants over generated inputs; the machine determines many cases) and **model-based testing** (derive cases from a state model) to complement hand-designed cases where a behaviour is best expressed as a property or a model [R10], [R11]; machine-generated cases **MUST** still satisfy the foundation's determinism rule (a fixed seed reproduces a failure).

### Risk-based selection

- **MUST** select **which** cases to determine and run first by **risk** (likelihood × impact), because exhaustive testing is impossible; the highest-risk behaviours get cases first [R13].

### The iterative-feedback rule

- **MUST** treat case determination as **recurring across the cycle**, not only up front. The phase **MUST** produce a new case when:
  - a **defect** is confirmed in analysis—write a **failing regression case that reproduces it before it's fixed** [R1], [R14];
  - a **coverage gap** is surfaced by execution;
  - an **exploratory finding** warrants a scripted case;
  - a **requirement change** adds new behaviour (and retires cases for removed behaviour).

### Case quality bar

- **MUST** require each determined case to be **independent** (no ordering or shared-state dependency), **deterministic by design**, scoped to **one clear behaviour**, **intention-revealing** in name, and to assert **observable behaviour** rather than implementation detail [R12].
- **MUST NOT** create **redundant or overlapping** cases, and **MUST NOT** over-specify a case beyond the behaviour it verifies; redundancy and over-specification raise maintenance cost and cause false breakages.

### Traceability

- **MUST** maintain the **requirement → TC-ID** traceability as a **single project-level matrix artefact** (not per-case frontmatter alone) so coverage of requirements—including which requirements have *zero* cases—is auditable and diff-able in one place, per the foundation's traceability chain [R12]. Per-case frontmatter records the reverse `case → requirement` edge and is the source the matrix is generated from and checked against; it doesn't substitute for the central matrix, because answering "which requirements are uncovered" from frontmatter alone requires scanning every case and can't surface a requirement that no case references.

## Acceptance Criteria

- [ ] The phase is defined as deciding which cases are needed and designing them, referencing `test-case-derivation` for requirement-derived derivation and deferring tier placement to the tier model
- [ ] Inputs (requirements, coverage gaps, defects, exploratory findings, changed behaviour) and outputs (cases with TC-ID + chosen tier) match the foundation's phase-1 contract
- [ ] The three technique families are recognised, and the core black-box techniques (EP, BVA, decision tables, state-transition, use-case, pairwise) are required where they fit, cited to ISTQB
- [ ] Structure-based coverage is bound as a guide to missing cases, never a numeric target (Goodhart), cited to Fowler
- [ ] Example Mapping / Specification by Example / BDD and test-first are required (SHOULD) as example-driven determination
- [ ] Property-based and model-based testing are permitted (MAY) with the determinism constraint
- [ ] Risk-based selection (likelihood × impact) is required
- [ ] The iterative-feedback rule is binding: a regression case for every confirmed defect (write the failing case first), plus coverage-gap, exploratory, and requirement-change cases
- [ ] The case quality bar (independent, deterministic-by-design, one behaviour, intention-revealing, observable behaviour, non-redundant, no over-specification) is required
- [ ] A requirement → TC-ID traceability matrix is required as a single central project-level artefact (per-case frontmatter is its source, not a substitute)
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-cycle-foundation/`: the cycle, the loop, and this phase's inter-phase contract
- [R2] `spec/project/test-case-derivation/`: the requirement → abstract-case derivation technique this phase references
- [R3] `spec/project/test-pyramid-foundation/`: owns which tier a case lands at
- [R4] `spec/project/quality-gate/`: executes cases; its coverage report feeds back into this phase
- [R5] ISTQB / ASTQB, *Black-box Test Techniques* (the technique families; EP, BVA, decision tables, state-transition, use-case): <https://astqb.org/4-2-black-box-test-techniques/>
- [R6] ISTQB, *Boundary Value Analysis* white paper (2-value / 3-value; off-by-one defect class): <https://istqb.org/wp-content/uploads/2025/10/Boundary-Value-Analysis-white-paper.pdf>
- [R7] Martin Fowler, *TestCoverage* (coverage as a guide to missing tests, not a target): <https://martinfowler.com/bliki/TestCoverage.html>
- [R8] Matt Wynne / Cucumber, *Example Mapping* (rules → examples → questions): <https://cucumber.io/docs/bdd/example-mapping/>
- [R9] G. Adzic, *Specification by Example*: <https://www.manning.com/books/specification-by-example>
- [R10] *Hypothesis*: property-based testing (invariants over generated inputs): <https://hypothesis.readthedocs.io/>
- [R11] *quickcheck-state-machine*: model-based testing from a state model: <https://hackage.haskell.org/package/quickcheck-state-machine>
- [R12] ISTQB Glossary, *test case* / *traceability matrix* (case quality; requirement → case traceability): <https://istqb-glossary.page/test-case/>
- [R13] *Risk-based testing* (likelihood × impact selection): <https://en.wikipedia.org/wiki/Risk-based_testing>
- [R14] *Write a failing test that reproduces the bug before fixing it*: <https://martinfowler.com/articles/testing-culture.html>
- [R15] `spec/project/behavior-driven-development/`: the full tool-neutral BDD standard this SHOULD operationalizes (collaborative discovery, scenario language, step-definition principles, and the test-case-document-to-scenario derivation)

## Open Questions

- Should the phase require a minimum technique set per case type (for example BVA + EP on any bounded numeric input), or stay advisory on which techniques apply?
- Where property-based testing applies, should the phase elevate it from MAY to SHOULD for pure functions with clear invariants, mirroring the unit tier's open question?
- ~~Does the requirement → TC-ID matrix live in a single project artefact, or is per-case frontmatter (as `test-case-derivation` already emits) sufficient as the traceability record?~~ **Settled (2026-07-24): one central artefact.** The matrix lives in a single project-level artefact (see the traceability requirement above); per-case frontmatter is the reverse-edge source it's built from and checked against, not a substitute. The audit question the matrix exists to answer—"which requirements have no case?"—is a coverage-*gap* question, and a gap is precisely a requirement that *no* frontmatter references; only a central artefact keyed by requirement can surface it without scanning every case, and only one diffable artefact keeps the coverage state reviewable in one place.
