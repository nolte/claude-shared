# Test Cycle Foundation

Status: draft

## Context

Testing isn't a one-shot activity that happens after code is written: it's a **recurring, iterative cycle** that runs continuously while a feature is built and maintained. This spec owns that cycle. Where `spec/project/test-pyramid-foundation/` answers *what to test and at which tier* (the structural dimension), this foundation answers *how the work of testing flows over time* (the process dimension)—the two are orthogonal and compose: every turn of the cycle operates within the tier model.

The cycle has **four phases** that chain and loop:

1. **Case determination**: decide which test cases are needed (from requirements, from coverage gaps, from defects found, from changed behaviour) and at which tier each lands.
2. **Execution**: run the cases and collect raw results.
3. **Result analysis**: interpret the results: pass, real failure, flake, coverage gap, or a missing case.
4. **Code adaptation**: given a red or missing case, determine and apply the minimal code change that satisfies it (or change the case in a deliberate, reviewable step when the case itself was wrong).

These map onto the classic **red-green-refactor** loop of test-driven development generalised to any tier and any point in a feature's life [R6], [R7]: a determined-and-failing case is *red*, a code adaptation that makes it pass is *green*, and the loop repeats. The defining property this spec encodes is the **loop**: phase 4 returns to phase 2 (re-execute), and phase 3 feeds back into phase 1 (a discovered defect becomes a new regression case; a coverage gap becomes a new case). The cycle terminates only on an explicit exit condition, never by weakening a test to force a pass.

This foundation is the **apex of a small process family**: it owns the loop, the inter-phase contracts, and the termination rule, and defers each phase's internal best practices to its own per-phase spec. Those per-phase specs are **process specs that reference existing capability specs as their realisations** rather than restating them.

**Relationship to the existing specs.** This foundation and its phase specs are a process layer over capabilities that already exist; the boundary is by responsibility:

- `spec/project/test-pyramid-foundation/` [R1]—the tier model the cycle runs within (orthogonal: structure vs process).
- `spec/project/test-cycle-case-determination/` [R2] (phase 1) references `spec/project/test-case-derivation/` for requirement-to-abstract-case derivation.
- `spec/project/test-cycle-execution/` [R3] (phase 2) references `spec/project/quality-gate/` and the tier specs' execution placement.
- `spec/project/test-cycle-result-analysis/` [R4] (phase 3) references `spec/project/e2e-test-automation/`'s `e2e-result-reviewer` and `spec/project/workflow-health/` for failure triage.
- `spec/project/test-cycle-code-adaptation/` [R5] (phase 4) is the net-new phase: turning a red case into the right code change.

Readers: spec authors writing the four phase specs on top of this foundation; skill and agent authors building the per-phase develop/execute/analyse tooling; developers and reviewers who run the cycle and need a shared vocabulary for which phase they're in and when the cycle is done.

## Goals

- Own the **iterative test cycle** as a first-class, recurring process: four phases that chain and loop, distinct from the tier model
- Define the **inter-phase contracts** (each phase's inputs and outputs) so the phases compose into a loop rather than four disconnected activities
- Make the **feedback edges** explicit: analysis produces new cases (phase 3 → phase 1) and drives code changes (phase 3 → phase 4), and code adaptation re-enters execution (phase 4 → phase 2)
- Encode the **termination rule** and the **no-cheating invariant** (never weaken a test to force a green)
- Define the **per-phase spec contract** so the four phase specs stay structurally consistent and reference existing capability specs instead of duplicating them
- Keep the whole family **tool- and tier-agnostic**: the cycle runs the same shape whether the case lands at the unit tier or the E2E tier

## Non-Goals

- Specifying the internal best practices of any one phase—each phase gets its own spec built on this foundation's per-phase contract
- Restating the capability specs the phases reference (`test-case-derivation`, `quality-gate`, `e2e-test-automation`, `workflow-health`)—those remain authoritative for their capability
- Owning the tier model or the test-double taxonomy—those belong to `spec/project/test-pyramid-foundation/` [R1]
- Mandating a specific workflow tool, runner, or methodology brand (TDD/BDD/ATDD): the cycle is the shared shape those methodologies share, stated tool-agnostically
- Building the per-phase skills and agents—this family declares the phases and their contracts; the artefacts are authored separately under `spec/claude/`

## Requirements

### The four phases and the loop

- **MUST** define the test cycle as four ordered phases (case determination, execution, result analysis, code adaptation) that **loop**: code adaptation returns to execution, and the cycle repeats until an exit condition holds.
- **MUST** treat the cycle as **recurring and continuous**, run at every tier and throughout a feature's life (not a one-time post-coding step), generalising the red-green-refactor loop of test-driven development to any tier [R6], [R7].
- **MUST** keep the cycle **orthogonal to the tier model**: a single turn of the cycle concerns one or more cases at their chosen tiers per `spec/project/test-pyramid-foundation/` [R1]; the cycle is the process, the tier model is the structure.

### Inter-phase contracts

- Each per-phase spec **MUST** declare its **inputs and outputs** so the phases chain deterministically:
  - **Case determination** outputs a set of test cases (each with a TC-ID and a chosen tier) that are expected to fail or be absent until satisfied.
  - **Execution** consumes the cases and outputs raw results (pass / fail / error, plus coverage and protocol artefacts where the tier produces them).
  - **Result analysis** consumes the results and outputs a **classification** per case: pass, real failure, flake, coverage gap, or missing case.
  - **Code adaptation** consumes a red or missing classification and outputs a **code change** (or a deliberate case change), which re-enters execution.
- A phase spec **MUST** make its output consumable by the next phase without out-of-band knowledge, so the loop is mechanical, not tacit.

### Feedback edges

- **MUST** define the feedback edges as first-class, not exceptions:
  - **Analysis → case determination** (phase 3 → phase 1): a real defect found in analysis **MUST** yield a new **regression case** that reproduces it before it's fixed; a coverage or behaviour gap yields a new case [R6].
  - **Analysis → code adaptation** (phase 3 → phase 4): a confirmed real failure routes to code adaptation, not to weakening the test.
  - **Code adaptation → execution** (phase 4 → phase 2): every code change re-enters execution; a change is never assumed correct without re-running the cases.
- **MUST** require a **regression case for every fixed defect** (write the failing case first, then make it pass), so the cycle accumulates coverage of real-world failures over time [R6].

### Termination and the no-cheating invariant

- **MUST** define explicit **exit conditions** for a cycle turn: every required case is green, no previously-green case regressed, and the coverage / mutation signal is acceptable per `spec/project/test-pyramid-foundation/`'s coverage governance. Absent those, the cycle continues.
- **MUST NOT** terminate the cycle by **weakening, deleting, or skipping a test to force a green**; a failing case is resolved by a code adaptation (phase 4) or by a *deliberate, reviewable* case change when the case itself was demonstrably wrong—never by a silent escape. This is the cycle's central integrity rule.
- **MUST** route a **flake** (a case that passes and fails without a code change) to quarantine-and-fix per `spec/project/test-pyramid-foundation/`'s determinism rule, not to a retry-until-green loop.

### Per-phase spec contract (the meta-contract)

- Every **per-phase spec MUST** define, at minimum: its **purpose and scope boundary**; its **inputs and outputs** (per §Inter-phase contracts); the **best practices** it requires (each grounded in cited sources); the **capability specs it references** as realisations and the boundary against them; its **feedback edges** into the other phases; and its **canonical anti-patterns**.
- A per-phase spec **MUST** reference rather than restate an existing capability spec where one covers its work, and **MUST** declare the boundary by responsibility.

### Traceability across the cycle

- **MUST** preserve the foundation's requirement → TC-ID → test traceability across every phase, so a case can be followed from determination through execution, analysis, and the code change that satisfied it.

## Acceptance Criteria

- [ ] The spec defines the four ordered phases (case determination, execution, result analysis, code adaptation) and the loop (phase 4 → phase 2; repeat until exit)
- [ ] The cycle is framed as recurring/continuous and generalising red-green-refactor, with the tier model declared orthogonal
- [ ] Each phase's inputs and outputs are specified so the phases chain mechanically into a loop
- [ ] The feedback edges (analysis → case determination, analysis → code adaptation, code adaptation → execution) are first-class, and a regression case for every fixed defect is required
- [ ] Explicit exit conditions are defined, and the no-cheating invariant (never weaken/skip a test to force green) is a MUST NOT
- [ ] Flakes route to quarantine-and-fix, not retry-until-green
- [ ] The per-phase spec meta-contract enumerates what each phase spec must define, including referencing (not restating) the existing capability specs
- [ ] The relationship section maps each phase to its referenced capability spec (case-determination → test-case-derivation; execution → quality-gate; analysis → e2e-result-reviewer / workflow-health; code-adaptation → net-new)
- [ ] Traceability requirement → TC-ID → test is required across all phases
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-pyramid-foundation/`: the tier model the cycle runs within (structure vs process)
- [R2] `spec/project/test-cycle-case-determination/`: phase 1; references `spec/project/test-case-derivation/`
- [R3] `spec/project/test-cycle-execution/`: phase 2; references `spec/project/quality-gate/`
- [R4] `spec/project/test-cycle-result-analysis/`: phase 3; references `e2e-result-reviewer` and `spec/project/workflow-health/`
- [R5] `spec/project/test-cycle-code-adaptation/`: phase 4 (net-new)
- [R6] Martin Fowler, *TestDrivenDevelopment* (red-green-refactor; a failing test drives the next change; regression test for a bug): <https://martinfowler.com/bliki/TestDrivenDevelopment.html>
- [R7] Martin Fowler, *The Practical Test Pyramid* (the test loop across tiers): <https://martinfowler.com/articles/practical-test-pyramid.html>

## Open Questions

- Should the cycle foundation declare a default **granularity of a cycle turn** (one case, one feature, one PR), or leave it per-project and per-tier?
- Do the four phases each get a develop/execute/analyse skill/agent triad, or does the cycle itself get one orchestrator skill that drives the loop and dispatches to per-phase capabilities (the existing `e2e-*` artefacts and `quality-gate` already cover parts of phases 2–3)?
- Where the "deliberate, reviewable case change" path is taken (the case was wrong), should the foundation require a recorded rationale tying it to a requirement change, to keep the no-cheating invariant auditable?
