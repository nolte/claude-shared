# Test Cycle: Code Adaptation

Status: draft

## Context

Code adaptation is **phase 4** of the iterative test cycle owned by `spec/project/test-cycle-foundation/`: given a confirmed real failure or a missing/red case that analysis (phase 3) handed over, it determines and applies the **minimal correct code change that makes the case pass**, then re-enters execution (phase 2) to verify. It's the cycle's *green* step, generalised from test-driven development to any tier and any trigger.

It's the one **net-new** phase of the cycle family—the other three reference an existing capability spec, but turning a red case into the right production change has no prior spec. What it must not become is a way to *force* a green: the foundation's central **no-cheating invariant** (never weaken, delete, skip, or special-case a test to make it pass) is inherited here and made concrete. The production change must satisfy the **behaviour** the test asserts, not merely silence one assertion.

This spec fills the foundation's **per-phase meta-contract** (purpose and scope boundary, inputs and outputs, required best practices, referenced capability specs, feedback edges, anti-patterns). It's deliberately tool- and tier-agnostic.

**Relationship to the other specs.** Bounded by responsibility:

- `spec/project/test-cycle-foundation/` [R1] owns the cycle and the no-cheating exit rule this phase makes concrete. This spec details phase 4.
- `spec/project/test-cycle-result-analysis/` [R2] (phase 3) hands this phase a **confirmed real failure**; this phase acts on it, it doesn't classify.
- `spec/project/test-cycle-execution/` [R3] (phase 2) re-runs the change to verify it; this phase never assumes green without re-execution.
- `spec/project/test-cycle-case-determination/` [R4] (phase 1) owns the **reviewable case-change path** when the test itself was wrong—that routes there, it's **not** a code hack here.

Readers: spec authors completing the cycle family; skill and agent authors building a code-adaptation capability; developers turning a red test green; reviewers checking that a change fixed the root cause and didn't game the test.

## Goals

- Make the change the **simplest correct one** that satisfies the case, then refactor under green
- Require fixing the **root cause, not the symptom**, and writing the **general** solution rather than overfitting to the example
- Make the foundation's **no-cheating / test-integrity invariant** concrete: satisfy the asserted behaviour, never weaken or special-case the test
- Keep **refactoring behaviour-preserving** and separate from behaviour change, with the suite as the safety net
- Require **verify-by-re-execution** (re-enter phase 2; all green, no regression) and a small, reviewable change
- Route a wrong-test correction to phase 1 (a reviewable case change), not to a code hack—no duplication

## Non-Goals

- **Classifying** a failure (deciding it's a real defect): phase 3 (`test-cycle-result-analysis`) [R2]
- **Running** the tests to verify: phase 2 (`test-cycle-execution`) [R3] (this phase triggers it, doesn't own it)
- **Correcting a wrong test**: that's a reviewable case change in phase 1 (`test-cycle-case-determination`) [R4], not a code change here
- Mandating a specific language, editor, or refactoring tool: techniques are named only as illustrative examples

## Requirements

### Purpose and scope boundary

- **MUST** define this phase as **determining and applying the minimal correct code change that makes a confirmed-red case pass**, as phase 4 of the cycle [R1].
- **MUST** act only on a **confirmed real failure** (or a missing case) routed from `spec/project/test-cycle-result-analysis/` [R2]; it doesn't re-classify.
- **MUST** route a **wrong test** to phase 1's reviewable case-change path [R4], never resolve it by hacking the code to match a wrong assertion.

### Inputs and outputs (the phase-4 contract)

- **MUST** consume, as input, a phase-3 classification of `real-failure` (or `missing-case`) for a TC-ID, with its supporting evidence (trace, diff, reproducer).
- **MUST** produce, as output, a **code change** that re-enters execution (phase 2); the change is the production edit, never an edit that weakens the case.

### The green step: Simplest change first

- **MUST** make the **simplest change that could possibly work** to get the case green, then improve under green; the production code is written **in response to a failing test**, not ahead of it [R5].
- **MAY** use the recognised green strategies by confidence (Beck) [R6]:
  - **Obvious Implementation**: type the real code directly when it's obvious.
  - **Fake It**: return a constant to get green, then generalise.
  - **Triangulation**: generalise the implementation only once **two or more examples** force it.

### Root cause, not symptom; no over-fitting

- **MUST** fix the **root cause**, not the symptom: a change that swallows an exception, special-cases the failing input, or otherwise patches around the defect without correcting it's forbidden.
- **MUST** write the **general** solution, not one that only satisfies the current example; **Triangulation** is the discipline that forces generality, and **property-based** cases (which assert over generated inputs) resist over-fitting because no single hard-coded value satisfies them [R7].

### The no-cheating / test-integrity invariant

- **MUST NOT** make a case pass by **weakening, deleting, skipping, or hard-coding to the test's expected value**; the change must satisfy the **behaviour** the case asserts, not just that one assertion. This is the foundation's no-cheating invariant made concrete for phase 4 [R1].
- **MUST** distinguish **legitimate generalisation** of the implementation from **special-casing the test's inputs**: returning the right answer for the general class is a fix; returning a constant matched to the test input (beyond a transient Fake-It step on the way to generalising) is gaming the test.
- **MUST** take the **reviewable case-change path** (route to phase 1) when the case itself was demonstrably wrong, with a recorded rationale, rather than silently changing an assertion to match the code.

### Refactor under green

- **SHOULD** refactor after the case is green: apply **small, behaviour-preserving transformations** to improve structure, with the suite as the safety net—refactoring **MUST NOT** change observable behaviour [R8], [R9].
- **MUST NOT** **mix refactoring with a behaviour change** in the same step; refactor only while green, and make behaviour changes as their own red-green step [R9], [R10].

### Regression-driven fix

- **MUST**, when the trigger is a defect found in analysis, make the new **failing regression case** (written first in phase 1) pass **while keeping every prior case green**; the green regression case is the proof the defect is fixed and stays fixed [R10], [R11].

### Verify by re-execution and review

- **MUST NOT** assume the change is correct: it **MUST** re-enter execution (phase 2) and **all** cases **MUST** be green with **no regression** before the cycle turn can exit [R3], [R11].
- **MUST** keep the change **small and reviewable**, and **SHOULD** have it reviewed (by a human or an automated reviewer) for correctness and for not having gamed the test, consistent with the project's pull-request review.

### Traceability

- **MUST** key the change to the **TC-IDs** it satisfies, so the production edit chains back through analysis and the case to the requirement, closing the cycle's traceability.

## Acceptance Criteria

- [ ] The phase is defined as determining/applying the minimal correct code change for a confirmed-red case (phase 4), acting only on a phase-3 real-failure/missing-case, and routing a wrong test to phase 1
- [ ] Inputs (phase-3 `real-failure`/`missing-case` + evidence) and output (a code change that re-enters execution, never a test-weakening edit) match the foundation's phase-4 contract
- [ ] The green step requires the simplest change first (in response to a failing test), with Beck's Obvious Implementation / Fake It / Triangulation strategies recognised
- [ ] Fixing the root cause not the symptom is required, and over-fitting is forbidden with Triangulation and property-based cases as the anti-over-fitting discipline
- [ ] The no-cheating invariant is concrete: no weakening/deleting/skipping/hard-coding-to-the-expected-value; satisfy behaviour not one assertion; the legitimate-generalisation-vs-special-casing distinction is drawn
- [ ] The reviewable case-change path (test was wrong → phase 1, recorded rationale) is required instead of a code hack
- [ ] Refactor-under-green is behaviour-preserving and not mixed with behaviour change, cited to Fowler
- [ ] The regression-driven fix (new failing case green + all prior green) is required, cited
- [ ] Verify-by-re-execution (re-enter phase 2; all green, no regression) and a small reviewable change are required
- [ ] The change is keyed to TC-IDs for traceability, and the boundary against phases 1/2/3 and the foundation is explicit
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-cycle-foundation/`: the cycle and the no-cheating exit rule this phase makes concrete
- [R2] `spec/project/test-cycle-result-analysis/`: phase 3; hands this phase a confirmed real failure
- [R3] `spec/project/test-cycle-execution/`: phase 2; re-runs the change to verify it
- [R4] `spec/project/test-cycle-case-determination/`: phase 1; owns the reviewable case-change path when the test was wrong
- [R5] Martin Fowler, *TestDrivenDevelopment* (write functional code until the test passes, in response to a failing test): <https://martinfowler.com/bliki/TestDrivenDevelopment.html>
- [R6] Kent Beck, *Test-Driven Development by Example*: Fake It / Obvious Implementation / Triangulation: <https://relentlessdevelopment.wordpress.com/2014/06/18/make-it-run-make-it-right-the-three-implementation-strategies-of-tdd/>
- [R7] *Property-based testing* (properties over generated inputs resist over-fitting): <https://arxiv.org/pdf/2307.04346>
- [R8] Martin Fowler, *Refactoring* / *RefactoringMalapropism* (small behaviour-preserving transformations; refactoring doesn't change observable behaviour): <https://martinfowler.com/bliki/RefactoringMalapropism.html>
- [R9] Martin Fowler, *Opportunistic Refactoring* (only refactor while green; depends on a regression suite): <https://martinfowler.com/bliki/OpportunisticRefactoring.html>
- [R10] Martin Fowler, *Self-Testing Code* (write a test exposing the bug, then fix; the suite as safety net): <https://martinfowler.com/bliki/SelfTestingCode.html>
- [R11] *Regression testing* (a fix keeps prior behaviour green): <https://en.wikipedia.org/wiki/Regression_testing>

## Open Questions

- What concrete signals best distinguish **legitimate generalisation** from **special-casing the test's inputs**: can the phase name a checkable heuristic, or does it stay a review judgement?
- When a fix genuinely requires an **existing test's expectation to change** (the old assertion encoded a now-removed behaviour), how does the phase keep that on the reviewable case-change path and out of the forbidden test-weakening category?
- Should the phase mandate **Triangulation or a property-based case** for any non-trivial generalisation, to make over-fitting structurally hard, or leave it advisory?
