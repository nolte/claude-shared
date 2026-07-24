# Test Cycle: Execution

Status: draft

## Context

Execution is **phase 2** of the iterative test cycle owned by `spec/project/test-cycle-foundation/`: it consumes the cases that phase 1 determined, runs them, and emits raw results for phase 3 to analyse. Because the cycle re-executes constantly (every code adaptation re-enters execution), this phase is the one whose **speed and determinism** decide whether the whole cycle is trustworthy and fast enough to live with.

It's a **process spec that references existing capability specs**, not a restatement of them. `spec/project/quality-gate/` already owns the single recognisable invocation that runs lint + typecheck + test and tabulates the outcome; this spec doesn't restate that. It frames execution as the recurring run-time discipline—deterministic/hermetic execution, isolation, parallel/selective speed, staged CI placement, flake handling, and the structured result-emission contract—that the gate and the tier runners realise.

This spec fills the foundation's **per-phase meta-contract** (purpose and scope boundary, inputs and outputs, required best practices, referenced capability specs, feedback edges, anti-patterns). It's deliberately tool- and tier-agnostic.

**Relationship to the other specs.** Bounded by responsibility:

- `spec/project/test-cycle-foundation/` [R1] owns the cycle and this phase's inter-phase contract. This spec details phase 2.
- `spec/project/quality-gate/` [R2] owns the single-invocation gate (lint + typecheck + test) and its output table; this spec references it as the executor of the fast tiers and **MUST NOT** restate its invocation contract.
- `spec/project/test-pyramid-foundation/` [R3] owns the determinism rule and each tier's execution placement; this spec applies them at run time, it doesn't redefine them.
- `spec/project/workflow-health/` [R4] triages a *red CI run*: that interpretation is phase 3 (result analysis), not this phase; execution emits raw results, analysis classifies them.

Readers: spec authors writing the sibling phase specs; skill and agent authors building an execution capability; developers and CI engineers wiring how tests run; reviewers checking that execution is deterministic, isolated, fast, staged, and emits a structured result.

## Goals

- Make **deterministic, hermetic execution** the run-time bar: same input, same result, regardless of machine, order, or environment
- Require **isolation and any-order** execution, with readiness-condition waits instead of bare sleeps
- Get **speed** from parallelisation/sharding and test selection, since the cycle re-executes constantly
- Stage execution in CI: fast tiers gate the PR, slow/broad tiers run in a dedicated stage or nightly
- Handle flakes by **bounded retry + tracked quarantine**, never retry-until-green
- Emit a **structured, machine-readable per-case result** as the phase-2 output contract
- Reference `quality-gate` as the gate executor and the tier specs for placement—no duplication

## Non-Goals

- Restating the single-invocation gate (lint + typecheck + test) and its output table: owned by `spec/project/quality-gate/` [R2]
- **Interpreting** results (classifying pass/fail/flake/defect): phase 3 (result analysis)
- Triaging a red CI run: owned by `spec/project/workflow-health/` [R4], invoked from phase 3
- **Determining** which cases to run (that's phase 1) or the **code change** for a failure (phase 4)
- Mandating a specific runner, CI system, or report format: tools and formats are named only as illustrative examples

## Requirements

### Purpose and scope boundary

- **MUST** define this phase as **running the determined cases and emitting raw results**, as phase 2 of the cycle [R1]; it executes, it doesn't interpret.
- **MUST NOT** restate the `quality-gate` single-invocation contract or output table; this phase **MUST** reference `spec/project/quality-gate/` [R2] as the executor of the fast tiers.
- **MUST** apply `spec/project/test-pyramid-foundation/`'s determinism rule and each tier's execution placement at run time rather than redefining them [R3].

### Inputs and outputs (the phase-2 contract)

- **MUST** consume, as input, the set of cases from phase 1 (TC-IDs and chosen tiers).
- **MUST** emit, as output, a **structured, machine-readable result per case**: pass / fail / error / skip, plus failure message and stack trace, timing, coverage data where the tier produces it, and the screenshot/protocol artefacts at the E2E tier—so phase 3 can analyse it without out-of-band knowledge [R13]. Standard formats (for example TAP's `ok`/`not ok` with YAML diagnostics, or JUnit XML) are illustrative.

### Deterministic and hermetic execution

- **MUST** make execution **deterministic**: the same input gives the same result regardless of machine, order, time, or network weather; a non-deterministic (flaky) test is useless for regression and erodes trust across the whole suite [R5].
- **MUST** control the run-time environment to achieve this: **wrap the clock** (freeze/substitute time), control randomness, replace remote/external services with test doubles (validated by the contract tier), and isolate shared state [R5].
- **SHOULD** run tests **hermetically**: each run brings its own dependencies and doesn't depend on external mutable state—so a run is reproducible and parallel-safe [R9].

### Isolation, ordering, and readiness waits

- **MUST** keep tests **isolated** so any execution order works, with per-test setup and teardown; **SHOULD** run in **randomised order** to surface hidden inter-test dependencies.
- **MUST NOT** use **bare sleeps** to wait for asynchronous results or dependency startup; poll a **readiness condition** (small interval, bounded wait limit) or use a callback [R5], [R14].
- **MUST NOT** execute against a **shared, mutable, long-lived** environment; ephemeral real dependencies at the integration tier follow the same wait-on-readiness rule [R14].

### Speed: Parallelisation, selection, caching

- **SHOULD** run tests in **parallel and shard** them across workers to keep the cycle's feedback fast [R8].
- **MAY** use **test impact analysis / predictive test selection** to run only the tests affected by a change while preserving regression signal (Meta reports running roughly a third of dependent tests while catching over 99.9% of faulty changes)—provided the full suite still runs on a schedule so selection never silently drops coverage [R7].
- **SHOULD** rely on **reproducible builds** so cross-machine test/build caching is safe (a cached result is valid only if the inputs are bit-for-bit reproducible) [R9].

### Staged CI execution

- **MUST** stage execution by tier: the **fast tiers** (static, unit, component, narrow integration, contract) **MUST** gate the pull request, and the **slow/broad tiers** (E2E, broad integration, performance) **SHOULD** run in a dedicated stage or nightly, per `spec/project/test-pyramid-foundation/`'s CI-gating model and the tier specs' placement [R3], [R10].
- **SHOULD** keep the PR-gating stage fast (a ~10-minute commit-build guideline) and run the most-relevant or fastest specs **first** (fail-fast) so feedback arrives early; whether the run then short-circuits or completes to collect all failures is a project choice [R10], [R11].

### Flakiness handling at execution time

- **MUST NOT** **retry a test until it goes green**: retrying a test until it passes hides real flakiness and ships a broken signal [R6], [R12].
- **MUST** own **flake detection** and leave **flake classification** to phase 3: this phase produces the observation, phase 3 assigns the class. The split is what keeps the invariant "a single green re-run doesn't clear a failure" enforceable, because the component that re-runs is never the component that decides the failure was harmless.
- **MUST** use a **bounded, flip-signal re-run** on a failing case: **N = 2 additional independent runs** (three observations in total), run in the same execution and under the same pinned command and environment. Two extra runs is the smallest N that can observe a flip in either direction while staying cheap enough to run on every red case; N = 1 can't distinguish a flip from a coincidence, and larger N buys confidence the phase isn't entitled to spend, since classification is phase 3's job. A project **MAY** raise N (never lower it) and **MUST** record the value it used.
- **MUST** emit the **per-run outcome vector** for that case (for example `fail, pass, fail`) plus a derived `flip-observed: true|false` signal as part of the structured result, and **MUST NOT** itself label the case `flaky` or `real`, collapse the vector to its best outcome, or let a green re-run replace the original red in the emitted result.
- **MUST** **quarantine** a known-flaky test (exclude it from the gating signal while tracking it as a defect to fix) rather than letting it block the gate or be silently re-run forever [R5], [R12].

### Reproducibility and pinning

- **MUST** pin the runner, tool, and dependency versions so an execution is reproducible across machines and over time, and **SHOULD** record the exact command and environment that produced a result, so a failure can be re-run identically by phase 3 [R9].

### Traceability

- **MUST** key each emitted result to the **TC-ID** of the case it ran, so the result chains back through the foundation's traceability to the requirement, and forward into analysis.

## Acceptance Criteria

- [ ] The phase is defined as running cases and emitting raw results (not interpreting them), referencing `quality-gate` as the fast-tier executor and deferring determinism/placement to the tier foundation
- [ ] Inputs (cases with TC-IDs/tiers) and outputs (structured per-case result: pass/fail/error/skip + message/trace + timing + coverage + E2E artefacts) match the foundation's phase-2 contract, with TAP/JUnit named as illustrative
- [ ] Deterministic + hermetic execution is required, with clock-wrapping, randomness/network control, and shared-state isolation, cited to Fowler/Bazel
- [ ] Isolation + randomised order is required, and bare sleeps are forbidden in favour of readiness-condition waits (incl. ephemeral deps), with no shared mutable environment
- [ ] Parallelisation/sharding is required (SHOULD); test selection is permitted (MAY) only if the full suite still runs on a schedule; reproducible-build caching is referenced
- [ ] Staged CI execution gates the fast tiers on the PR and runs slow/broad tiers in a dedicated stage/nightly, with a fast-PR-stage + fail-fast guideline
- [ ] Retry-until-green is forbidden; the bounded flip-signal re-run is detection-only at a fixed N = 2 additional independent runs, emitting the per-run outcome vector plus a `flip-observed` signal and never a `flaky`/`real` label; known flakes are quarantined-and-tracked
- [ ] Reproducibility via pinning + recorded command/environment is required
- [ ] Each result is keyed to a TC-ID for traceability
- [ ] The boundary against `quality-gate` (single-invocation gate), `workflow-health` (red-CI triage = phase 3), and phases 1/3/4 is explicit
- [ ] EN and DE versions are structurally identical (same headings, requirement count, acceptance-criteria count) and the spec index lists the new slug

## References

- [R1] `spec/project/test-cycle-foundation/`: the cycle and this phase's inter-phase contract
- [R2] `spec/project/quality-gate/`: the single-invocation gate (lint + typecheck + test) and output table this phase references
- [R3] `spec/project/test-pyramid-foundation/`: the determinism rule and per-tier execution placement / CI-gating model
- [R4] `spec/project/workflow-health/`: red-CI triage (invoked from phase 3, not this phase)
- [R5] Martin Fowler, *Eradicating Non-Determinism in Tests* (flaky tests; clock-wrapping; doubles; no bare sleeps; quarantine): <https://martinfowler.com/articles/nonDeterminism.html>
- [R6] Google Testing Blog, *Flaky Tests at Google and How We Mitigate Them*: <https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html>
- [R7] Meta Engineering, *Predictive Test Selection* (run affected tests, preserve regression signal): <https://engineering.fb.com/developer-tools/predictive-test-selection/>
- [R8] Playwright, *Test sharding* (parallel execution across workers): <https://playwright.dev/docs/test-sharding>
- [R9] Bazel, *Hermeticity* / *Remote caching* (hermetic, reproducible execution enables safe caching): <https://bazel.build/basics/hermeticity>
- [R10] Martin Fowler, *Continuous Integration* (staged build, ~10-minute commit build): <https://martinfowler.com/articles/continuousIntegration.html>
- [R11] GitLab, *Fail-fast testing* (run most-relevant specs first): <https://docs.gitlab.com/ci/testing/fail_fast_testing/>
- [R12] Atlassian, *Taming test flakiness* (detect + quarantine, not retry-until-green): <https://www.atlassian.com/blog/atlassian-engineering/taming-test-flakiness-how-we-built-a-scalable-tool-to-detect-and-manage-flaky-tests>
- [R13] *Test Anything Protocol (TAP)* / JUnit XML (structured machine-readable results): <https://testanything.org/tap-version-14-specification.html>
- [R14] Testcontainers, *Startup and wait strategies* (readiness-based waits for ephemeral dependencies): <https://java.testcontainers.org/features/startup_and_waits/>

## Open Questions

- Should the portfolio set a concrete PR-gating-stage time budget (for example the ~10-minute guideline) as a requirement, or keep it advisory and per-project?
- Should test impact analysis / predictive selection be elevated from MAY to SHOULD for large suites, given its proven cost saving—and what's the required cadence for the full-suite safety run?
- ~~Is the bounded flip-signal retry better owned here (execution emits a `flaky` flag) or in phase 3 (analysis decides flake vs real)—where exactly does the flake *classification* live versus the flake *detection*?~~ **Settled (2026-07-24): detection here, classification in phase 3.** Execution runs the bounded re-run at a fixed N = 2 additional independent runs and emits the per-run outcome vector plus `flip-observed`; it never emits a `flaky` label. `spec/project/test-cycle-result-analysis/` consumes that vector together with cross-run history and assigns the class. Separating the two puts the "presume real until evidence" judgement in the one phase whose entire job is classification, and denies the re-running component any authority to explain its own red away—the exact failure mode that turns a bounded re-run into retry-until-green.
