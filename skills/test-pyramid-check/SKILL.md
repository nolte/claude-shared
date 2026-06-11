---
name: test-pyramid-check
description: Audit a feature's or module's test-tier completeness against spec/project/e2e-test-automation/ — are the applicable tiers (unit, integration, contract/API, E2E) present, is fast-tier coverage gated, and does the E2E tier follow the spec's disciplines (page-object encapsulation, condition-based waits, screenshot checkpoints, markers, TC-ID traceability)? Detects the stack, globs the test files per tier, and returns a gap report. Invoke when the user asks to "check the test pyramid," "audit test-tier completeness," "verify all test levels exist," after a feature is implemented, or before a release; also handles equivalent German-language requests. Don't use to scaffold E2E tests (use e2e-test-generator), to review/repair an E2E suite (use e2e-test-reviewer), to review a run's screenshots (use e2e-result-reviewer), or to run the lint/typecheck/test gate (use quality-gate).
argument-hint: "[feature or module, e.g. REQ-013 or checkout]"
tags: [quality-gate, audit]
phase: quality
summary: "Audits a feature's test-tier completeness (unit/integration/contract/E2E) and E2E discipline against the e2e-test-automation spec, returning a gap report."
summary_de: "Prüft die Teststufen-Vollständigkeit (Unit/Integration/Contract/E2E) und E2E-Disziplin eines Features gegen die e2e-test-automation-Spec und liefert einen Lückenbericht."
use_when:
  - "you want to verify a feature has all applicable test tiers present"
  - "you want the E2E tier audited for the spec's disciplines before a release"
dont_use_when:
  - situation: "you want to scaffold a new E2E suite"
    alternative: e2e-test-generator
  - situation: "you want to run the lint/typecheck/test gate"
    alternative: quality-gate
see_also:
  - e2e-test-generator
  - e2e-test-reviewer
  - quality-gate
---

# Test Pyramid Check: $ARGUMENTS

Audit whether `$ARGUMENTS` (a feature or module) carries the test tiers it should, and whether its E2E tier follows the disciplines the spec requires. This skill **reads and reports** — it generates and modifies nothing.

Implements `spec/project/e2e-test-automation/` §"Test-tier completeness (the pyramid)" and the E2E-discipline requirements. The spec fixes *that* the tiers must exist and be gated; the numeric coverage targets are project-declared, so read them from the project rather than assuming a number.

## German trigger phrases

Also triggers on equivalent German-language requests, including "Testpyramide prüfen", "Teststufen-Vollständigkeit auditieren", "prüfe ob alle Testebenen vorhanden sind". Detect the user's language and respond in it; the report table uses English headers so it stays diffable.

## Step 1 — Read the spec and detect the stack

Read `spec/project/e2e-test-automation/` (the tier model and E2E disciplines). Detect the project's stack from its manifests and layout (e.g. `pyproject.toml` + `tests/`, `package.json` + `*.test.ts`, `go.mod` + `*_test.go`) so you glob the right paths for each tier. Read the project's declared coverage targets where they live (CI config, `pyproject.toml` `[tool.coverage]`, a project test spec) — do not assume a fixed percentage.

## Step 2 — Locate each tier (in parallel)

Glob the test files for `$ARGUMENTS` across the applicable tiers, scoping by the feature/module name. Map each to a tier:

| Tier | Scope | Typical signal |
|---|---|---|
| Unit | business logic in isolation | unit test files next to / mirroring the module |
| Integration | critical paths with real dependencies | integration test dir, testcontainers, DB fixtures |
| Contract/API | each endpoint, happy + error paths | API/contract test files (only if the system exposes an API) |
| E2E | user journeys through the real UI | the E2E suite (reference profile: `tests/e2e/`) |

A tier that does not apply (no API surface → no contract tier) is **not** a gap; record it as `n/a` with the reason.

## Step 3 — Check fast-tier gating

Confirm the fast tiers exist for `$ARGUMENTS`'s business logic, and that a coverage gate is actually wired (CI fails below the project's declared floor) rather than merely aspirational. Report the declared target and whether it is enforced — not a number you invented.

## Step 4 — Check E2E discipline

If an E2E tier exists for `$ARGUMENTS`, check it against the spec's disciplines (grep-level, not a deep code review — that is `e2e-test-reviewer`):

- Page-object encapsulation — no raw driver element-lookups in test bodies
- Condition-based waits — no fixed-duration sleeps in tests
- Screenshot checkpoints present
- At least one marker per test
- TC-ID traceability in docstrings

Flag violations by file; for a deep per-line review or repairs, hand off to `e2e-test-reviewer`.

## Step 5 — Report

```markdown
# Test pyramid review: {feature/module}

## Tier overview
| Tier | Present | Tests | Assessment |
|------|---------|-------|------------|
| Unit | yes/no/n-a | N | ... |
| Integration | yes/no/n-a | N | ... |
| Contract/API | yes/no/n-a | N | ... |
| E2E | yes/no/n-a | N | ... |

## Fast-tier gating
{declared target, enforced yes/no, source}

## E2E discipline
{page objects / waits / screenshots / markers / TC-IDs — per check, with file refs}

## Gaps (prioritised)
{numbered list of missing tiers / ungated coverage / discipline violations}

## Verdict
{spec-conformant, or N gaps — with the highest-priority gap named}
```

## Hard rules

1. Read and report only — never scaffold, edit, or run tests. Scaffolding is `e2e-test-generator`; repair is `e2e-test-reviewer`; running the gate is `quality-gate`.
2. A non-applicable tier is `n/a` with a reason, never a gap — don't demand an API tier from a system with no API.
3. Report the project's *declared* coverage target and whether it is enforced; never invent a percentage.
4. Keep the E2E check at grep/structure level; route deep review and fixes to `e2e-test-reviewer`.
5. When `spec/project/e2e-test-automation/` and this skill disagree, the spec wins; this skill needs the update.

## Why this is a skill, not an agent

- **Orchestration role:** tier auditing is one step in a pre-release / post-feature flow; the gap report is meant to flow back into the conversation so the caller decides which gaps to close.
- **Interactivity:** the caller typically triages the gaps (fill now, defer) in the same conversation — skill bias.
- **Context-window impact is acceptable:** the work is glob + grep + a compact table, so subagent isolation would not pay for itself.
- **Counter-dimension (context-window, which favours an agent):** a very large suite means many file reads, but they are shallow (globs and greps, not full reads), so the volume stays manageable in-thread.
