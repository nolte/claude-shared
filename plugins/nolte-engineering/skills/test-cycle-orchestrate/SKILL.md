---
name: test-cycle-orchestrate
description: "Drives one or more turns of the iterative test cycle defined in spec/project/test-cycle-foundation/ — case determination → execution → result analysis → code adaptation → re-execute — dispatching each phase to its capability (test-case-extractor and the per-tier test-generators for cases, quality-gate for execution, test-result-analyzer for analysis, test-code-adapter for the fix) and looping until an explicit exit condition holds. Enforces the cycle's integrity rules: a regression case before fixing a defect, a flake quarantined not retried-until-green, and the no-cheating invariant (never weaken/skip a test to force a pass). Invoke when the user asks to run the test cycle for a feature, drive a feature to green, or iterate determine-execute-analyse-fix. Don't use to run the gate once (use quality-gate), to scaffold tests without the loop (use a tier generator), or to classify results without acting (use test-result-analyzer). Supports resume per `spec/claude/resumable-work/`."
argument-hint: "[feature, module, or failing case to drive to green]"
tags: [quality-gate]
phase: quality
summary: "Drives the iterative test cycle (determine → execute → analyse → adapt → re-execute) for a feature, dispatching each phase and looping to green under the no-cheating invariant."
summary_de: "Treibt den iterativen Test-Zyklus (ermitteln → ausführen → analysieren → anpassen → erneut ausführen) für ein Feature, dispatcht jede Phase und schleift bis Grün unter der No-Cheating-Invariante."
use_when:
  - "you want the test cycle run for a feature, looping determine-execute-analyse-fix to green"
  - "you want a confirmed failure driven through analysis and a verified code fix"
dont_use_when:
  - situation: "you want to run the lint/typecheck/test gate once, not the loop"
    alternative: quality-gate
  - situation: "you want to scaffold tests for a tier without running the loop"
    alternative: unit-test-generator
see_also:
  - test-result-analyzer
  - test-code-adapter
  - quality-gate
  - test-case-extractor
resumable: true
---

# Test Cycle Orchestrate: $ARGUMENTS

Drive the iterative test cycle for `$ARGUMENTS` (a feature, module, or failing case): determine cases → execute → analyse results → adapt code → re-execute, looping until an explicit exit condition holds. This skill **orchestrates**; each phase is performed by its capability, dispatched in turn, and the results flow back here so you decide whether to loop again.

Governed by `spec/project/test-cycle-foundation/` (the loop, the inter-phase contracts, the exit conditions, and the no-cheating invariant) and the four phase specs it references.

## Why this is a skill, not an agent

- **Orchestrator that chains other capabilities:** the cycle dispatches `test-case-extractor` / per-tier generators, `quality-gate`, `test-result-analyzer`, and `test-code-adapter` in a loop; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- **Mid-flow gating lives in the conversation:** the no-cheating decision, the "is this exit-ready or loop again" decision, and the wrong-test-routes-to-a-reviewable-case-change decision are per-turn user-visible gates an agent's fire-and-forget shape would lose.
- **Output flows back into the main conversation:** each phase's result (the classification, the applied fix, the re-run verdict) surfaces so the operator can steer.
- Counter-dimension considered: each individual phase is a self-contained agent (the generators, analyzer, adapter); the loop that sequences them is the orchestration, which stays a skill.

## The cycle

Run the loop for `$ARGUMENTS`. One turn:

### 1. Determine cases

Ensure the cases that should be green exist and currently fail or are absent. Dispatch `test-case-extractor` to derive abstract cases from a requirement, and the per-tier generator (`unit-test-generator`, `component-test-generator`, `integration-test-generator`, `contract-test-generator`, or `e2e-test-generator`) to scaffold the runnable test at the tier the foundation's lowest-tier-that-gives-confidence rule selects. When the trigger is a confirmed defect, a **failing regression case is written first**, and its red run is recorded as negative-verification evidence per `spec/project/test-falsifiability/` — the command plus the observed failure, carried into the run's audit trail.

### 2. Execute

Run the cases. Dispatch `quality-gate` (the fast tiers) and the project's tier runners; collect the structured per-case results. Honour the staged-execution model — fast tiers gate, slow/broad tiers run where the project places them.

On every red case, run the **bounded flip-signal re-run** mandated by `spec/project/test-cycle-execution/`: **N = 2 additional independent runs** of that case (three observations total), in the same execution under the same pinned command and environment. Emit the **per-run outcome vector** (for example `fail, pass, fail`) plus the derived `flip-observed: true|false` signal as part of the structured result. Detection only: never collapse the vector to its best outcome, never let a green re-run replace the original red, and never label the case `flaky` or `real` here — classification is step 3's job. A project may raise N (never lower it) and records the value used.

### 3. Analyse results

Dispatch `test-result-analyzer` to classify each non-pass into a routed category (real defect / flake / test bug / infra / stale dep / config drift) with evidence, handing it the execution-emitted per-run outcome vector and `flip-observed` signal from step 2 — analysis consumes that vector together with cross-run history and never re-runs a case itself. Route a flake to quarantine, a test bug back to step 1 as a reviewable case change, and infra/stale/config to the environment (via `workflow-health-triage`).

### 4. Adapt code

For each confirmed real failure, dispatch `test-code-adapter` to apply the minimal correct change that satisfies the asserted behaviour, fixing the root cause. The analyzer's classification and root-cause are a hypothesis, so this brief **MUST** authorise refutation per `spec/claude/dispatch-brief/`: the adapter may refute the diagnosed root cause with contradicting evidence and change nothing (or apply a narrower fix) rather than force the fix to fit, and that refutation is a valid result that re-enters step 3 (re-analyse) instead of a failed dispatch. The fix **re-enters step 2** (re-execute); never assume green without re-running.

**Optional review leg:** when the adaptation touched test code itself, dispatch the touched tier's `*-test-reviewer` agent (unit / component / integration / contract / e2e) as the review-and-repair counterpart before re-executing — mirroring the reviewer wiring the E2E tier already carries. When the adaptation added or changed assertions, readers, or helpers, this leg is not optional: the tier reviewer's falsifiability dimension (per `spec/project/test-falsifiability/`) must grade the touched tests before re-execution.

### Loop or exit

Repeat from step 2 until the **exit conditions** hold: every required case is green, no previously-green case regressed, and the coverage/mutation signal is acceptable per the foundation's coverage governance. Surface the per-turn state each round; stop when exit-ready, or hand back when a turn cannot make progress (for example a fix needs a product decision).

## Hard rules

1. **Never** make a case pass by weakening, deleting, skipping, or hard-coding to its expected value; resolve a red case by a code adaptation (step 4) or, when the test was wrong, a reviewable case change (step 1) — never a silent escape. This is the cycle's central integrity rule.
2. **Always** write a failing regression case before fixing a confirmed defect, recording its red run as negative-verification evidence per `spec/project/test-falsifiability/`, so the cycle accumulates coverage of real failures over time.
3. **Never** retry a flaky test until it goes green; the only permitted re-running is step 2's bounded flip-signal re-run (fixed N, detection-only, vector-emitting); route a confirmed flake to quarantine-and-track, not to the gating signal.
4. **Never** declare a turn complete without re-execution: a code change re-enters step 2 and all cases must be green with no regression before exit.
5. **Never** restate a phase's internals here; dispatch its capability (`test-case-extractor` / tier generators, `quality-gate`, `test-result-analyzer`, `test-code-adapter`) and orchestrate the loop. When a phase spec disagrees with this skill, the spec wins; propose a skill update rather than diverging.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/test-cycle-orchestrate/<run-id>.yml` after every successful phase boundary and user-approval gate. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and fail-closed semantics are load-bearing in the spec; don't duplicate those rules here.
