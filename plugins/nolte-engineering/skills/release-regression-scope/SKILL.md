---
name: release-regression-scope
description: Determines the release-relevant regression/E2E test scope from a release change-set per spec/project/release-regression-scope/, so a team runs targeted-but-safe regression before rollout. The default `scope` operation resolves the release range, dispatches the read-only release-regression-scope-scanner to attribute each change to its impacted areas via traceability inversion (change → requirement/TC-ID → verifying tests), selects the minimal tier/test set (E2E emphasised) covering those areas, widens non-attributable changes to worst-case full-area regression, and reports an auditable scope (in-scope areas, selected tests, exclusions + rationale, residual risk). A missing verifying test is a coverage-gap blocker. Invoke to scope release regression, pick targeted E2E, or gate a rollout on a fast subset; also German. Don't use to derive test cases (test-case-extractor), run tests (quality-gate), audit pyramid shape (test-pyramid-check), or drive the release (release-publish-trigger). Supports resume.
tags: [quality-gate, review]
phase: quality
summary: "Determines the minimal-but-complete release regression/E2E scope from the change-set via traceability inversion, selecting covering tests and widening non-attributable changes to worst-case."
summary_de: "Bestimmt den minimalen-aber-vollständigen Release-Regressionsumfang aus dem Change-Set via Traceability-Inversion; wählt abdeckende Tests, verbreitert nicht-attribuierbare auf Worst-Case."
use_when:
  - "you want to scope release regression tests from the actual change-set before a rollout"
  - "you want targeted E2E selection that still guarantees complete coverage of every impacted area"
  - "you want an auditable rollout decision: in-scope areas, selected tests, exclusions with rationale, residual risk"
dont_use_when:
  - situation: "You want to derive new test cases for a requirement or a single cycle"
    alternative: test-case-extractor
  - situation: "You want to actually run the tests / the quality gate"
    alternative: quality-gate
  - situation: "You want to audit a feature's test-tier completeness"
    alternative: test-pyramid-check
  - situation: "You want to publish or drive the release"
    alternative: release-publish-trigger
see_also:
  - release-regression-scope-scanner
  - test-pyramid-check
resumable: true
---

# Release Regression Scope

Determine the release-relevant regression/E2E test scope from a release's change-set, so a rollout gates on a subset that's **zielgenau** (only impacted areas), **zeitnah** (fast enough to ship), and **vollständig-im-Bereich** (complete within every impacted area). Implements `spec/project/release-regression-scope/`. The skill *selects* over tests that already exist and produces an auditable report; it never writes, runs, or derives tests, and never drives the release.

## German trigger phrases

- „Regressions-Umfang für das Release bestimmen"
- „welche E2E-Tests muss ich vor dem Rollout laufen lassen?"
- „zielgenauen Testumfang aus dem Change-Set ableiten"
- „das Release-Gate auf die betroffenen Bereiche eingrenzen"

## User-language policy

Detect the operator's language and respond in it. All `git`, `gh`, and `Agent(subagent_type=…)` invocations stay English; the report's machine-readable fields (area IDs, TC-IDs, `subagent_type`) stay English so the trail is grep-able. The report's prose is written in the operator's language.

## Tooling (optional GitHub MCP)

When resolving the release range from merged pull requests, prefer the connected GitHub MCP server's read tools (`github:list_pull_requests`, `github:search_pull_requests`, `github:pull_request_read`) and fall back to the `gh` commands, per `spec/claude/mcp-tool-preference/`. `gh` stays authoritative; output is identical whichever path is taken (spec R9). This skill runs in the main session and inherits its MCP tools, so no `tools:` grant is needed.

## Inputs

- The release range (base…head): the last published release tag to the release-candidate tip, or an operator-supplied range. When ambiguous, confirm the range with the operator before scanning.
- The repository's test suite and its test↔requirement traceability, plus the requirement/feature index under `project/requirements/` and `project/features/`.

## Operations

### `scope` (default, read-only)

1. **Resolve the release range.** Determine base…head (last release → RC tip, or operator-supplied). Enumerate the change-set: touched paths and merged PRs (MCP-preferred, `gh` fallback).
2. **Dispatch attribution.** Dispatch the read-only `release-regression-scope-scanner` agent with the change-set; it returns the per-change attribution inventory (impacted areas, verifying tests per area with tier, non-attributable residual-risk list).
3. **Select the minimal scope.** For each impacted area, select the minimal tier/test set that covers its functional requirements, emphasising E2E for user-journey coverage (spec R4).
4. **Apply the completeness rule.** An impacted area is *fully covered* only when every functional requirement has an existing, green verifying test at the appropriate tier (R5). A missing verifying test surfaces as a **coverage-gap blocker** for that area (R6) — never a silent pass.
5. **Widen non-attributable changes.** For every non-attributable change, require the full regression set of all plausibly-impacted area(s) and record a residual-risk note (R3) — never narrow silently.
6. **Emit the report** (see Report shape). Present it to the operator. The skill stops at the report; running the selected tests is `quality-gate`'s job and shipping is the `release-*` layer's.

## Report shape

```
# Release Regression Scope — <base>…<head>

## Verdict
<SHIP-READY once the selected scope is green | BLOCKED: coverage gaps in N area(s)>

## In-scope areas
- <area> — requirements <ids> — selected tests: <test @ tier>, …

## Deliberately excluded
- <area/path> — <rationale for exclusion>

## Coverage gaps (blockers)
- <area> — requirement <id> has no green verifying test at <tier>

## Residual risk
- <non-attributable change> — widened to full <area> regression — <reason>
```

## Gotchas

Per `spec/claude/skill-management/` §Gotchas.

- **This skill selects; it never derives.** Manufacturing a new test case for an uncovered requirement is `test-case-extractor` / `test-cycle-case-determination`, not this skill. An uncovered requirement is a coverage-gap blocker, not a prompt to write a test here.
- **Non-attributable never means narrower.** The safe direction for an unmapped change is *wider* (full-area regression + residual-risk note), never a guessed subset. Silent narrowing violates spec R3.
- **A missing verifying test is a blocker, not a pass.** An impacted area with a requirement that has no green test is *not* covered (R5/R6); reporting it as in-scope-and-passing is the failure mode this skill exists to prevent.
- **The scanner is read-only and range-agnostic.** The skill resolves the release range and hands the scanner the refs; the scanner attributes only. Don't expect the scanner to reach the GitHub API.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/release-regression-scope/<run-id>.yml` after the range is confirmed and after the attribution inventory is collected, so an interrupted run resumes without re-scanning. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot (the release range and repository) matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate them here.

## Hard rules

- **Never** derive new test cases, run tests, or modify any file — this skill selects over existing tests and reports.
- **Never** narrow the scope for a non-attributable change; widen to full-area regression and record the residual risk (spec R3).
- **Never** report an impacted area as covered when a functional requirement lacks a green verifying test at the appropriate tier; surface it as a coverage-gap blocker (spec R5, R6).
- **Never** gate the release on an unimpacted area (violates *zielgenau*), and never leave an impacted area partially covered (violates *vollständig-im-Bereich*).
- **Always** attribute via the existing test↔requirement traceability (change → requirement/TC-ID → verifying tests), delegating the read-only attribution pass to `release-regression-scope-scanner`.
- When `spec/project/release-regression-scope/` disagrees with this skill, the spec wins. Propose updating this skill rather than diverging silently.

## Why this is a skill, not an agent

- **Mid-flow operator dialogue:** confirming an ambiguous release range and presenting the auditable scope for the rollout decision are interactive gates; an agent's fire-and-forget shape would miss them.
- **Orchestrator pattern:** the work is *resolve range → dispatch scanner → select → verdict → report*; the read-only attribution is delegated to the scanner agent while the skill stays in the main thread and chains it.
- **Persistent artifact + resume:** the report and the resumable envelope are persistent state a skill owns.
- **Counter-dimension:** the attribution pass alone is a self-contained, context-heavy scan — that half is the `release-regression-scope-scanner` agent; the selection, verdict, and operator-facing report stay in this skill.
