---
title: test-cycle-orchestrate
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# test-cycle-orchestrate

> Drives the iterative test cycle (determine → execute → analyse → adapt → re-execute) for a feature, dispatching each phase and looping to green under the no-cheating invariant.

_Drives one or more turns of the iterative test cycle defined in spec/project/test-cycle-foundation/ — case determination → execution → result analysis → code adaptation → re-execute — dispatching each phase to its capability (test-case-extractor and the per-tier test-generators for cases, quality-gate for execution, test-result-analyzer for analysis, test-code-adapter for the fix) and looping until an explicit exit condition holds. Enforces the cycle's integrity rules: a regression case before fixing a defect, a flake quarantined not retried-until-green, and the no-cheating invariant (never weaken/skip a test to force a pass). Invoke when the user asks to run the test cycle for a feature, drive a feature to green, or iterate determine-execute-analyse-fix. Don't use to run the gate once (use quality-gate), to scaffold tests without the loop (use a tier generator), or to classify results without acting (use test-result-analyzer). Supports resume per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-engineering`
- **Phase:** 6 Quality (`quality`)
- **Tags:** `quality-gate`
- **Source:** [skills/test-cycle-orchestrate/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/test-cycle-orchestrate/SKILL.md)

## Use when

- you want the test cycle run for a feature, looping determine-execute-analyse-fix to green
- you want a confirmed failure driven through analysis and a verified code fix

## Don't use when

- **you want to run the lint/typecheck/test gate once, not the loop** → [`quality-gate`](quality-gate.md)
- **you want to scaffold tests for a tier without running the loop** → [`unit-test-generator`](../../agents/nolte-engineering/unit-test-generator.md)

## See also

- [`test-result-analyzer`](../../agents/nolte-engineering/test-result-analyzer.md)
- [`test-code-adapter`](../../agents/nolte-engineering/test-code-adapter.md)
- [`quality-gate`](quality-gate.md)
- [`test-case-extractor`](../../agents/nolte-engineering/test-case-extractor.md)

---

## Test Cycle Orchestrate: $ARGUMENTS

Drive the iterative test cycle for `$ARGUMENTS` (a feature, module, or failing case): determine cases → execute → analyse results → adapt code → re-execute, looping until an explicit exit condition holds. This skill **orchestrates**; each phase is performed by its capability, dispatched in turn, and the results flow back here so you decide whether to loop again.

Governed by `spec/project/test-cycle-foundation/` (the loop, the inter-phase contracts, the exit conditions, and the no-cheating invariant) and the four phase specs it references.

### Why this is a skill, not an agent

- **Orchestrator that chains other capabilities:** the cycle dispatches [`test-case-extractor`](../../agents/nolte-engineering/test-case-extractor.md) / per-tier generators, [`quality-gate`](quality-gate.md), [`test-result-analyzer`](../../agents/nolte-engineering/test-result-analyzer.md), and [`test-code-adapter`](../../agents/nolte-engineering/test-code-adapter.md) in a loop; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- **Mid-flow gating lives in the conversation:** the no-cheating decision, the "is this exit-ready or loop again" decision, and the wrong-test-routes-to-a-reviewable-case-change decision are per-turn user-visible gates an agent's fire-and-forget shape would lose.
- **Output flows back into the main conversation:** each phase's result (the classification, the applied fix, the re-run verdict) surfaces so the operator can steer.
- Counter-dimension considered: each individual phase is a self-contained agent (the generators, analyzer, adapter); the loop that sequences them is the orchestration, which stays a skill.

### The cycle

Run the loop for `$ARGUMENTS`. One turn:

#### Phase 1 — Determine cases

Ensure the cases that should be green exist and currently fail or are absent. Dispatch [`test-case-extractor`](../../agents/nolte-engineering/test-case-extractor.md) to derive abstract cases from a requirement, and the per-tier generator ([`unit-test-generator`](../../agents/nolte-engineering/unit-test-generator.md), [`component-test-generator`](../../agents/nolte-engineering/component-test-generator.md), [`integration-test-generator`](../../agents/nolte-engineering/integration-test-generator.md), [`contract-test-generator`](../../agents/nolte-engineering/contract-test-generator.md), or [`e2e-test-generator`](../../agents/nolte-engineering/e2e-test-generator.md)) to scaffold the runnable test at the tier the foundation's lowest-tier-that-gives-confidence rule selects. When the trigger is a confirmed defect, a **failing regression case is written first**.

#### Phase 2 — Execute

Run the cases. Dispatch [`quality-gate`](quality-gate.md) (the fast tiers) and the project's tier runners; collect the structured per-case results. Honour the staged-execution model — fast tiers gate, slow/broad tiers run where the project places them.

#### Phase 3 — Analyse results

Dispatch [`test-result-analyzer`](../../agents/nolte-engineering/test-result-analyzer.md) to classify each non-pass into a routed category (real defect / flake / test bug / infra / stale dep / config drift) with evidence. Route a flake to quarantine, a test bug back to phase 1 as a reviewable case change, and infra/stale/config to the environment (via [`workflow-health-triage`](../nolte-shared/workflow-health-triage.md)).

#### Phase 4 — Adapt code

For each confirmed real failure, dispatch [`test-code-adapter`](../../agents/nolte-engineering/test-code-adapter.md) to apply the minimal correct change that satisfies the asserted behaviour, fixing the root cause. The fix **re-enters phase 2** (re-execute); never assume green without re-running.

#### Loop or exit

Repeat from phase 2 until the **exit conditions** hold: every required case is green, no previously-green case regressed, and the coverage/mutation signal is acceptable per the foundation's coverage governance. Surface the per-turn state each round; stop when exit-ready, or hand back when a turn cannot make progress (for example a fix needs a product decision).

### Hard rules

1. **Never** make a case pass by weakening, deleting, skipping, or hard-coding to its expected value; resolve a red case by a code adaptation (phase 4) or, when the test was wrong, a reviewable case change (phase 1) — never a silent escape. This is the cycle's central integrity rule.
2. **Always** write a failing regression case before fixing a confirmed defect, so the cycle accumulates coverage of real failures over time.
3. **Never** retry a flaky test until it goes green; route a confirmed flake to quarantine-and-track, not to the gating signal.
4. **Never** declare a turn complete without re-execution: a code change re-enters phase 2 and all cases must be green with no regression before exit.
5. **Never** restate a phase's internals here; dispatch its capability ([`test-case-extractor`](../../agents/nolte-engineering/test-case-extractor.md) / tier generators, [`quality-gate`](quality-gate.md), [`test-result-analyzer`](../../agents/nolte-engineering/test-result-analyzer.md), [`test-code-adapter`](../../agents/nolte-engineering/test-code-adapter.md)) and orchestrate the loop. When a phase spec disagrees with this skill, the spec wins; propose a skill update rather than diverging.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/test-cycle-orchestrate/<run-id>.yml` after every successful phase boundary and user-approval gate. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and fail-closed semantics are load-bearing in the spec; don't duplicate those rules here.
