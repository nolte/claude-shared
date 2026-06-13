---
title: test-pyramid-check
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# test-pyramid-check

> Audits a feature's tier completeness against the test-pyramid-foundation taxonomy (unit/component/integration/contract/E2E) and E2E discipline against e2e-test-automation; returns a gap report.

_Audit a feature's or module's test-tier completeness against the closed functional-tier taxonomy in spec/project/test-pyramid-foundation/ (are the applicable tiers — unit, component, integration, contract, E2E — present and written at the lowest tier that gives confidence?) and whether the E2E tier follows the disciplines in spec/project/e2e-test-automation/ (page-object encapsulation, condition-based waits, screenshot checkpoints, markers, TC-ID traceability). Detects the stack, globs the test files per tier, and returns a gap report. Invoke when the user asks to "check the test pyramid," "audit test-tier completeness," "verify all test levels exist," after a feature is implemented, or before a release; also handles equivalent German-language requests. Don't use to scaffold E2E tests (use e2e-test-generator), to review/repair an E2E suite (use e2e-test-reviewer), to review a run's screenshots (use e2e-result-reviewer), or to run the lint/typecheck/test gate (use quality-gate)._

- **Plugin:** `nolte-shared`
- **Phase:** 6 Quality (`quality`)
- **Tags:** `quality-gate`, `audit`
- **Source:** [skills/test-pyramid-check/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/test-pyramid-check/SKILL.md)

## Use when

- you want to verify a feature has all applicable test tiers present
- you want the E2E tier audited for the spec's disciplines before a release

## Don't use when

- **you want to scaffold a new E2E suite** → [`e2e-test-generator`](../../agents/nolte-shared/e2e-test-generator.md)
- **you want to run the lint/typecheck/test gate** → [`quality-gate`](quality-gate.md)

## See also

- [`e2e-test-generator`](../../agents/nolte-shared/e2e-test-generator.md)
- [`e2e-test-reviewer`](../../agents/nolte-shared/e2e-test-reviewer.md)
- [`quality-gate`](quality-gate.md)

## Referenced by

- [`component-test-reviewer`](../../agents/nolte-shared/component-test-reviewer.md)
- [`e2e-test-reviewer`](../../agents/nolte-shared/e2e-test-reviewer.md)
- [`unit-test-reviewer`](../../agents/nolte-shared/unit-test-reviewer.md)

---

## Test Pyramid Check: $ARGUMENTS

Audit whether `$ARGUMENTS` (a feature or module) carries the test tiers it should, and whether its E2E tier follows the disciplines the spec requires. This skill **reads and reports** — it generates and modifies nothing.

Implements the closed functional-tier taxonomy of `spec/project/test-pyramid-foundation/` (tier completeness) and the E2E-discipline requirements of `spec/project/e2e-test-automation/`. The foundation owns coverage governance — coverage is a guide, not a target — so read any project-declared coverage targets from the project rather than assuming a number.

### German trigger phrases

Also triggers on equivalent German-language requests, including "Testpyramide prüfen", "Teststufen-Vollständigkeit auditieren", "prüfe ob alle Testebenen vorhanden sind". Detect the user's language and respond in it; the report table uses English headers so it stays diffable.

### Step 1 — Read the spec and detect the stack

Read `spec/project/test-pyramid-foundation/` (the closed functional-tier taxonomy) and `spec/project/e2e-test-automation/` (the E2E disciplines). Detect the project's stack from its manifests and layout (e.g. `pyproject.toml` + `tests/`, `package.json` + `*.test.ts`, `go.mod` + `*_test.go`) so you glob the right paths for each tier. Read the project's declared coverage targets where they live (CI config, `pyproject.toml` `[tool.coverage]`, a project test spec) — do not assume a fixed percentage.

### Step 2 — Locate each tier (in parallel)

Glob the test files for `$ARGUMENTS` across the applicable tiers, scoping by the feature/module name. Map each to a tier:

| Tier | Scope | Typical signal |
|---|---|---|
| Unit | one unit of behaviour in isolation | unit test files next to / mirroring the module |
| Component | a single shippable component in isolation (externals doubled) | component / render test files; service-in-isolation tests |
| Integration | code against one real external collaborator | integration test dir, Testcontainers, DB fixtures |
| Contract | a service-boundary agreement, no live partner | contract / pact test files (only where a service boundary exists) |
| E2E | user journeys through the real UI | the E2E suite (reference profile: `tests/e2e/`) |

These are the foundation's functional tiers above static analysis. The **static-analysis** tier (lint / type-check / format) is audited by the quality gate, not here. A tier that does not apply (no service boundary → no contract tier; no UI → no E2E) is **not** a gap; record it as `n/a` with the reason.

### Step 3 — Check fast-tier gating

Confirm the fast tiers exist for `$ARGUMENTS`'s business logic, and that a coverage gate is actually wired (CI fails below the project's declared floor) rather than merely aspirational. Report the declared target and whether it is enforced — not a number you invented.

### Step 4 — Check E2E discipline

If an E2E tier exists for `$ARGUMENTS`, check it against the spec's disciplines (grep-level, not a deep code review — that is [`e2e-test-reviewer`](../../agents/nolte-shared/e2e-test-reviewer.md)):

- Page-object encapsulation — no raw driver element-lookups in test bodies
- Condition-based waits — no fixed-duration sleeps in tests
- Screenshot checkpoints present
- At least one marker per test
- TC-ID traceability in docstrings

Flag violations by file; for a deep per-line review or repairs, hand off to [`e2e-test-reviewer`](../../agents/nolte-shared/e2e-test-reviewer.md).

### Step 5 — Report

```markdown
## Test pyramid review: {feature/module}

### Tier overview
| Tier | Present | Tests | Assessment |
|------|---------|-------|------------|
| Unit | yes/no/n-a | N | ... |
| Component | yes/no/n-a | N | ... |
| Integration | yes/no/n-a | N | ... |
| Contract | yes/no/n-a | N | ... |
| E2E | yes/no/n-a | N | ... |

### Fast-tier gating
{declared target, enforced yes/no, source}

### E2E discipline
{page objects / waits / screenshots / markers / TC-IDs — per check, with file refs}

### Gaps (prioritised)
{numbered list of missing tiers / ungated coverage / discipline violations}

### Verdict
{spec-conformant, or N gaps — with the highest-priority gap named}
```

### Hard rules

1. Read and report only — never scaffold, edit, or run tests. Scaffolding is [`e2e-test-generator`](../../agents/nolte-shared/e2e-test-generator.md); repair is [`e2e-test-reviewer`](../../agents/nolte-shared/e2e-test-reviewer.md); running the gate is [`quality-gate`](quality-gate.md).
2. A non-applicable tier is `n/a` with a reason, never a gap — don't demand an API tier from a system with no API.
3. Report the project's *declared* coverage target and whether it is enforced; never invent a percentage.
4. Keep the E2E check at grep/structure level; route deep review and fixes to [`e2e-test-reviewer`](../../agents/nolte-shared/e2e-test-reviewer.md).
5. When `spec/project/test-pyramid-foundation/` (tier taxonomy / completeness) or `spec/project/e2e-test-automation/` (E2E discipline) and this skill disagree, the spec wins; this skill needs the update.

### Why this is a skill, not an agent

- **Orchestration role:** tier auditing is one step in a pre-release / post-feature flow; the gap report is meant to flow back into the conversation so the caller decides which gaps to close.
- **Interactivity:** the caller typically triages the gaps (fill now, defer) in the same conversation — skill bias.
- **Context-window impact is acceptable:** the work is glob + grep + a compact table, so subagent isolation would not pay for itself.
- **Counter-dimension (context-window, which favours an agent):** a very large suite means many file reads, but they are shallow (globs and greps, not full reads), so the volume stays manageable in-thread.
