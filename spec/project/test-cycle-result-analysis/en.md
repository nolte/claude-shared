# Test Cycle: Result Analysis

Status: draft

## Context

Result analysis is **phase 3** of the iterative test cycle owned by `spec/project/test-cycle-foundation/`: it consumes the raw results that execution (phase 2) emitted and **classifies** each one so the cycle knows what to do next. Classification is the core job of this phase—a raw `fail` isn't actionable until it's understood as a real defect, a flake, a wrong test, or an environment problem, and each category routes a different next phase.

It's a **process spec that references existing capability specs**, not a restatement of them. `spec/project/e2e-test-automation/`'s `e2e-result-reviewer` agent already owns the **visual review of an E2E run's screenshots and protocol** against the requirement specs, and `spec/project/workflow-health/` already owns the **triage lanes of a red CI run** with its failure taxonomy; this phase references both and adds the cycle-level concern: turning results into a routed classification that drives the loop.

This spec fills the foundation's **per-phase meta-contract** (purpose and scope boundary, inputs and outputs, required best practices, referenced capability specs, feedback edges, anti-patterns). It's deliberately tool- and tier-agnostic.

**Relationship to the other specs.** Bounded by responsibility:

- `spec/project/test-cycle-foundation/` [R1] owns the cycle and this phase's inter-phase contract. This spec details phase 3.
- `spec/project/test-cycle-execution/` [R2] (phase 2) emits the raw results this phase consumes; this phase interprets, it doesn't run.
- `spec/project/workflow-health/` [R3] owns the red-CI triage lanes and the failure taxonomy (defect / flake / infra / stale pin / secret drift / other); this phase reuses that taxonomy and references it for CI-failure triage rather than restating it.
- `spec/project/e2e-test-automation/` [R4] owns visual E2E output review via `e2e-result-reviewer`; this phase references it for the E2E tier rather than restating it.

Readers: spec authors writing the sibling phase specs; skill and agent authors building a result-analysis capability; developers and reviewers reading test output; anyone deciding whether a red result is a code bug, a test bug, or noise.

## Goals

- Make **classification the mandatory first act** of analysis: no result drives an action until it carries a category
- Enforce **real-vs-flake discipline**: a failure isn't explained away as a flake without evidence, and a single green re-run doesn't clear it
- Require **root-cause** technique (read the diff/trace, bisect to the offending change, minimise to a reproducer)
- Treat **coverage as a guide** that feeds new cases back to phase 1 and **mutation score** as the stronger suite-quality signal
- Define the **routing output contract**: each classification routes to the right next phase
- Reference `e2e-result-reviewer` (visual review) and `workflow-health` (CI triage)—no duplication

## Non-Goals

- **Running** the tests or emitting raw results: phase 2 (`test-cycle-execution`) [R2]
- Owning the **red-CI triage lanes**: `spec/project/workflow-health/` [R3] (referenced here)
- Owning the **visual E2E output review**: `e2e-result-reviewer` in `spec/project/e2e-test-automation/` [R4] (referenced here)
- **Applying** the fix for a confirmed defect: phase 4 (`test-cycle-code-adaptation`)
- Mandating a specific analysis tool or dashboard: tools are named only as illustrative examples

## Requirements

### Purpose and scope boundary

- **MUST** define this phase as **interpreting raw results into a routed classification**, as phase 3 of the cycle [R1]; it analyses, it neither runs tests (phase 2) nor applies fixes (phase 4).
- **MUST** consume the structured per-case results emitted by `spec/project/test-cycle-execution/` [R2] without re-running them.

### Classification before action

- **MUST** make **classification the first act**: every non-pass result **MUST** be classified before any action is taken on it. The classes, aligned with `spec/project/workflow-health/`'s failure taxonomy [R3], are: **real defect** (in the code under test), **flake** (non-deterministic), **test bug** (the test itself is wrong), **infrastructure / environment**, **stale dependency**, and **config / secret drift**.
- **MUST** route each class to the next phase: a **real defect** → code adaptation (phase 4), with a **new regression case** added in phase 1 first; a **test bug** → case determination (phase 1) to correct the case; a **flake** → quarantine-and-track per the execution and foundation rules; **infra / stale dep / config drift** → fix the environment (out of the test-cycle phases, via `workflow-health`).
- **MUST NOT** take an action on an **unclassified** result (mute it, re-run it, or change code)—acting before classifying is the core anti-pattern of this phase.

### Real failure versus flake

- **MUST NOT** explain a failure away as a **flake without evidence**: a failure is presumed **real** until classification shows otherwise [R5].
- **MUST** establish flakiness by **independent re-runs and history**, not by a single re-run: a single green re-run **doesn't** clear a failure—a result that fails then passes with no change is evidence of flakiness *to be quarantined and fixed*, not of the original failure being safe to ignore [R5], [R6].
- **MUST** treat the **normalisation of flakiness** (routinely waving failures through as "probably flaky") as a trust-destroying anti-pattern, per the foundation's determinism rule.

### Root-cause analysis

- **MUST** localise a real failure from the evidence execution emitted: the **assertion diff** (expected vs actual), the **stack trace**, logs, and—at the E2E tier—the screenshots and protocol.
- **SHOULD** use **change bisection** (for example `git bisect`) to find the offending commit when the cause isn't obvious from the trace [R7].
- **SHOULD** reduce a failing case to a **minimal reproducer** so the cause is isolated and the eventual fix is verifiable [R8].

### Coverage and suite-quality analysis

- **MUST** read **coverage as a guide** that surfaces untested code, feeding a **new case back to phase 1**, never as a pass/fail number, per `spec/project/test-pyramid-foundation/`'s coverage governance and Fowler [R9].
- **SHOULD** use **mutation score** as the stronger suite-quality signal—surviving mutants indicate weak or missing assertions—read as a **trend**, not an absolute target [R10].

### Visual and CI-signal analysis (referenced capabilities)

- **MUST** route **visual / E2E output review** (rendered output, screenshots, protocol against the requirement specs) to `e2e-result-reviewer` in `spec/project/e2e-test-automation/` [R4]; this phase references it and **MUST NOT** restate its review discipline.
- **MUST** route **red-CI-run triage** (reading a CI failure, classifying it into the lanes) to `spec/project/workflow-health/` [R3]; this phase reuses that taxonomy and **MUST NOT** restate the lanes.
- **SHOULD** read **trends across runs**: deduplicating many failures with one root cause into one finding, and tracking pass-rate / flake-rate over time to spot a newly-flaky test or a systemic infra issue.

### Routing output (the phase-3 contract)

- **MUST** emit, per case, a **classification that routes to a next phase**: `pass` (done), `real-failure` (→ phase 4 + new regression case in phase 1), `test-bug` (→ phase 1), `flake` (→ quarantine), `coverage-gap` / `missing-case` (→ phase 1), `infra` / `stale-dep` / `config-drift` (→ environment fix via workflow-health).
- **MUST** make the classification **evidence-bearing** (the trace/diff/reproducer or the re-run history that justifies the class), so the routed next phase acts on a substantiated decision, not a guess.

### Traceability

- **MUST** key each classification to the **TC-ID** of the result it analysed, so the decision chains back to the requirement and forward to the case or code change it triggers.

## Acceptance Criteria

- [ ] The phase is defined as interpreting raw results into a routed classification (not running tests, not applying fixes), consuming execution's structured output
- [ ] Classification is mandatory before any action, using the workflow-health failure taxonomy (defect / flake / test-bug / infra / stale dep / config-secret drift), and acting on an unclassified result is forbidden
- [ ] Each class routes to a next phase (real defect → phase 4 + regression case in phase 1; test bug → phase 1; flake → quarantine; infra/stale/config → environment fix)
- [ ] Real-vs-flake discipline is required: presume real, no explaining-away without evidence, and a single green re-run doesn't clear a failure, cited to Google
- [ ] Root-cause via assertion diff / trace / logs / E2E artefacts, change bisection, and minimal reproducer is required, cited to git-bisect and reproducer guides
- [ ] Coverage is read as a guide feeding new cases (not a number), and mutation score is the stronger suite-quality signal read as a trend
- [ ] Visual/E2E review is routed to `e2e-result-reviewer` and red-CI triage to `workflow-health` (referenced, not restated), with cross-run trend/dedup analysis
- [ ] The routing output contract (per-case evidence-bearing classification → next phase) is defined
- [ ] Classifications are keyed to TC-IDs for traceability
- [ ] The boundary against execution (phase 2), code adaptation (phase 4), `e2e-result-reviewer`, and `workflow-health` is explicit
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-cycle-foundation/`: the cycle and this phase's inter-phase contract
- [R2] `spec/project/test-cycle-execution/`: phase 2; emits the raw results this phase consumes
- [R3] `spec/project/workflow-health/`: red-CI triage lanes and the failure taxonomy this phase reuses
- [R4] `spec/project/e2e-test-automation/`: visual E2E output review via `e2e-result-reviewer` (referenced)
- [R5] Google Testing Blog, *Test Flakiness—One of the Main Challenges of Automated Testing* (presume real; don't normalise flakiness): <https://testing.googleblog.com/2021/03/test-flakiness-one-of-main-challenges.html>
- [R6] Google Testing Blog, *Test Flakiness* (re-run independently; a pass doesn't clear a failure): <https://testing.googleblog.com/2020/12/test-flakiness-one-of-main-challenges.html>
- [R7] Git, *git-bisect* (binary-search the offending commit): <https://git-scm.com/docs/git-bisect>
- [R8] scikit-learn, *Crafting a minimal reproducer* (minimise a failing case to isolate the cause): <https://scikit-learn.org/stable/developers/minimal_reproducer.html>
- [R9] Martin Fowler, *TestCoverage* (coverage as a guide to missing tests, not a target): <https://martinfowler.com/bliki/TestCoverage.html>
- [R10] Codecov, *Mutation testing: ensuring coverage isn't a vanity metric* (mutation score as the stronger signal): <https://about.codecov.io/blog/mutation-testing-how-to-ensure-code-coverage-isnt-a-vanity-metric/>

## Open Questions

- How many independent re-runs (and over what window) should the phase require before classifying a failure as flake versus real—a fixed number, or a confidence threshold?
- Should the deduplication of many failures into one root cause be a required step with a named grouping key (for example stack-trace signature), or stay advisory?
- Where a classification is `test-bug`, should the phase require a recorded rationale tying the case change to a requirement, mirroring the foundation's no-cheating auditability question?
