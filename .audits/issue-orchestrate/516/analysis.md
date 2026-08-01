---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "516"
classification: "feature-request"
secondary-classes: ["spec-change"]
route: "direct"
status: draft
created: "2026-08-01"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #516 — feat(capability): error-tracking-audit scanner (post-dogfooding)
- **URL**: https://github.com/nolte/claude-shared/issues/516
- **Labels**: enhancement, spec
- **Linked items**: no linked PRs. Declared blockers: nolte/kamerplanter#777 (**CLOSED
  2026-07-29** via PR #859 — dogfooding complete) and nolte/k8s-home-lab#833 (**OPEN** —
  gates end-to-end validation only, explicitly not the static checks). The issue is
  therefore unblocked for its stated scope.
- **Prior art checked**: no `project/features/` entry, no `project/roadmap.md` item, and no
  open PR references #516. `spec/project/error-tracking/` exists (draft, `Portfolio-Scope:
  portfolio`) and is listed in `spec/README.md`; its §Open Questions names this capability
  as the one remaining open point. The `observability-audit` skill + `observability-audit-scanner`
  agent in `plugins/nolte-engineering/` are the sibling pattern the issue points at.

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: spec-change
- **Rationale**: the deliverable is a new capability (a read-only scanner agent plus a thin
  audit skill) in `nolte-engineering`; settling the governing spec's Open Question about
  that capability's shape rides along as the secondary spec change.

## Scope

- **In scope** — the statically checkable slice named in the issue, authored as one
  capability pair plus the spec settlement:
  1. Sentry-protocol-compatible SDK present in the dependency manifest **and** initialised
     at process entry (backend and frontend patterns).
  2. DSN sourced from environment/deployment configuration, never hardcoded; graceful
     no-DSN no-op.
  3. `environment` and `release` tagging wired from deployment metadata.
  4. PII controls: default-PII off plus a before-send scrubbing hook.
  5. A recorded, deliberate sampling decision (portfolio default: 100% for low-traffic
     services).
  6. Report format per `spec/claude/review-plan/` severities, mirroring the
     `observability-audit` sibling.
- **Out of scope**:
  - Runtime behaviour — events actually arriving, alert rules firing, triage-SLA
    adherence, retention actually configured on the server. These are surfaced as
    `[runtime-verify]`/advisory findings, never static hard fails, per the spec's
    static-verification philosophy.
  - Provisioning or operating a GlitchTip instance (nolte/k8s-home-lab#833 / #834).
  - The telemetry contract itself (owned by `observability-audit` /
    `spec/project/monitoring-observability/`), the PII-class and GDPR verdict (owned by
    `gdpr-data-protection-reviewer`), and CI failure triage (`workflow-health-triage`).
  - Any mechanical `apply` that rewrites a target repository's instrumentation;
    remediation is a specialist-implemented plan, as with the sibling.

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome (one capability pair plus the spec settlement that
  defines it), one PR strand, no new or retargeted roadmap item. The sibling capability
  (`observability-audit` + scanner) was delivered the same way in a single PR.
- **Pipeline hand-off**: n/a

## Requirements gate

No artefact exists under `project/requirements/` for error tracking. **Operator override
recorded 2026-08-01**: the issue body states the six statically checkable items, the report
format, the sibling pattern, and the out-of-scope boundary explicitly, and
`spec/project/error-tracking/` supplies the normative RFC 2119 requirements the checks bind
to. Understanding is grounded in those two artefacts rather than in an elicitation
interview; `requirements-elicit` was deliberately not dispatched.

## Work packages

### P1 — Settle the spec's audit-capability Open Question

- **Problem statement**: `spec/project/error-tracking/` §Open Questions still records the
  audit capability as "planned 2026-07-25, shape open" and names the concrete check set and
  report format as the one unresolved point. Authoring the capability without settling that
  entry leaves the spec contradicting what the repository ships.
- **Acceptance criteria**: the Open Question entry reads as settled with the date, the six
  statically checkable items, the static-vs-runtime carve-out, and the artefact names
  (`error-tracking-audit` skill, `error-tracking-audit-scanner` agent); `en.md` is canonical
  and `de.md` is a strictly synchronised translation with identical section structure and
  mirrored MUST keywords; `spec/README.md`'s row for the spec reflects the new revision
  date; `task test` and Vale stay green.
- **Touched files / artifacts**: `spec/project/error-tracking/en.md`,
  `spec/project/error-tracking/de.md`, `spec/README.md`
- **Specialist**: `nolte-shared:spec` (skill — its description names spec creation,
  translation, and index regeneration)
- **Depends on**: none

### P2 — Author the `error-tracking-audit-scanner` agent

- **Problem statement**: the detection half of the capability does not exist. Confirming
  error-tracking wiring means reading a high volume of low-value material (dependency
  manifests, process entrypoints, SDK init call sites, scrubbing hooks, deployment config,
  frontend runtime-config injection) across several services and languages — exactly the
  context-window pressure the sibling isolates into a read-only agent.
- **Acceptance criteria**: `plugins/nolte-engineering/agents/error-tracking-audit-scanner.md`
  exists with `distribution: plugin`, read-only tools only (`Read`, `Bash`, `Glob`, `Grep`)
  and the read-only-Bash justification section required by `spec/claude/agent-management/`;
  it detects per component the six in-scope checks, tags every finding `[static]` or
  `[runtime-verify]` with `file:line` attribution, and returns a structured inventory
  without assigning a verdict, writing a report, or editing anything; its `description`
  delimits it against `observability-audit-scanner`, `gdpr-data-protection-reviewer`, and
  the parent skill; `scripts/validate_skills.py` passes (≤ 1024-char `description`,
  ≤ 1536 combined with `when_to_use`).
- **Touched files / artifacts**: `plugins/nolte-engineering/agents/error-tracking-audit-scanner.md`
- **Specialist**: `Agent(subagent_type="nolte-claude-dev:claude-plugin-developer")` (its
  description names drafting a spec-conformant plugin artifact in this monorepo)
- **Depends on**: P1

### P3 — Author the `error-tracking-audit` skill

- **Problem statement**: the policy half — severity triage, the hard-fail rule, the
  persisted audit artefact, and the handover that turns gaps into a specialist-ready plan —
  has no home. Without it the scanner's inventory has no consumer and no report format.
- **Acceptance criteria**: `plugins/nolte-engineering/skills/error-tracking-audit/SKILL.md`
  exists with `tags: [audit]`, `phase: quality`, `resumable: true`, and a `see_also` naming
  the scanner; it defines an `audit` operation (dispatch the scanner, apply the hard-fail
  policy over the mandatory static checks, document `[runtime-verify]` items, render the
  report, persist `.audits/error-tracking-audit/error-tracking-YYYY-MM-DD.md` with scope,
  Git revision, and per-component verdict) and a `plan` operation dispatching
  `implementation-plan-author` with a refutation-authorising brief per
  `spec/claude/dispatch-brief/`; it declares no mechanical `apply`; severities follow
  `spec/claude/review-plan/`; the "why this is a skill, not an agent" rationale carries the
  counter-dimension; `scripts/validate_skills.py` passes including the ~5,000-token body cap.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/error-tracking-audit/SKILL.md`
- **Specialist**: `Agent(subagent_type="nolte-claude-dev:claude-plugin-developer")`
- **Depends on**: P1, P2

### P4 — Conformance review of the scanner agent

- **Problem statement**: a newly authored agent has to be held against
  `spec/claude/agent-management/` and `spec/claude/skill-vs-agent/` before it ships; the
  authoring dispatch is not its own reviewer.
- **Acceptance criteria**: `nolte-claude-dev:agent-review` reports no Critical finding for
  `error-tracking-audit-scanner`; every Warning is either fixed or recorded with a rationale
  in the PR's Risk / rollout notes.
- **Touched files / artifacts**: `plugins/nolte-engineering/agents/error-tracking-audit-scanner.md`
- **Specialist**: `nolte-claude-dev:agent-review` (skill)
- **Depends on**: P2

### P5 — Conformance review of the audit skill

- **Problem statement**: same gate on the skill half, against
  `spec/claude/skill-management/` and `spec/claude/skill-vs-agent/`.
- **Acceptance criteria**: `nolte-claude-dev:skill-review` reports no Critical finding for
  `error-tracking-audit`; every Warning is fixed or recorded with a rationale; any review
  plan it writes under `.audits/skill-review/` is closed or removed before the PR merges.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/error-tracking-audit/SKILL.md`
- **Specialist**: `nolte-claude-dev:skill-review` (skill)
- **Depends on**: P3

### P6 — Calibrate the check set against the dogfooding adopter

- **Problem statement**: the issue defers authoring until "a real adopter" exists precisely
  so the checks recognise real patterns rather than invented ones. An uncalibrated scanner
  reports false negatives against the very repository it was written for.
- **Acceptance criteria**: walking the scanner's documented procedure against
  `~/repos/github/kamerplanter` resolves all six checks to a finding with `file:line` for
  every in-house component (backend, inference-service, knowledge-service, frontend);
  specifically it recognises the shared-and-copied `kp_errortracking` module (an init
  helper one indirection away from the entrypoint), the dynamic-`import()` frontend SDK
  load, and the runtime-injected DSN from `runtimeConfig()` / the container entrypoint —
  none of which a naive "grep for `sentry_sdk.init` at the entrypoint" check would find.
  Any pattern the procedure misses is fixed in P2/P3, and the calibration result is
  recorded in the dispatch log.
- **Touched files / artifacts**: read-only against `~/repos/github/kamerplanter`; fixes land
  in the P2/P3 artefacts
- **Specialist**: no matching specialised agent — generalist remediation (the newly authored
  scanner is not yet loadable as a plugin agent in this session, so its procedure is walked
  by hand; this is validation of the new artefact, not a recurring portfolio gap)
- **Depends on**: P2, P3

## Dependency ordering

```text
P1 → P2 → P3
      ↓     ↓
     P4    P5
      └──┬──┘
         P6   (needs both artefacts; its fixes fold back into P2/P3)
```

Dispatch order: P1, P2, P3, then P4 and P5 (independent of each other), then P6.

## Risks

- **Routing-budget pressure.** The `nolte-engineering` plugin already carries ~37k characters
  of skill+agent `description` text, and the portfolio watches a ~15k-token routing budget.
  *Mitigation*: keep both new descriptions at sibling density, verify against
  `scripts/validate_skills.py`'s hard caps (1024 / 1536 chars), and prefer body-only prose
  for anything that does not drive routing.
- **Overlap with `observability-audit`.** That skill already audits the browser
  error-capture floor and that PII redaction is wired; a sloppy split produces two
  capabilities fighting over the same finding. *Mitigation*: mirror the spec's own neighbour
  delimitation in both artefacts' `dont_use_when` and body — this capability audits the
  error-tracking **tool layer** (SDK/DSN/environment/release/sampling), the sibling audits
  the telemetry contract.
- **Vale gate on the canonical spec.** `spec/**/en.md` is linted with the CI-pinned Vale
  3.15.2 under the Microsoft style: contractions are mandatory, em-dashes are unspaced in
  EN, and tool/package names need backticks. *Mitigation*: lint with the pinned binary
  before pushing; dispatch `nolte-shared:prose-vale-curator` on any residue. German terms
  never enter `en.md` and are never silenced via `accept.txt`.
- **Translation drift.** The DE file must mirror the EN structure and MUST keywords
  file-internally. *Mitigation*: P1 runs through `nolte-shared:spec`, which owns the
  in-sync-translation contract, rather than hand-editing one language.
- **Security-sensitive paths**: the diff is Markdown instruction artefacts and spec prose —
  no application code, no credential handling, no dependency change. `code-security-reviewer`
  and the `security-review` skill are therefore **not** required for this PR; the judgement
  is recorded here deliberately rather than skipped silently. The *content* nonetheless
  concerns PII controls, so P4/P5 must confirm the artefacts never render a GDPR verdict
  (owned by `gdpr-data-protection-reviewer`) and only check that scrubbing is wired.
- **Worktree tooling friction.** Running `task` inside a fresh worktree can trip the
  untrusted-Taskfile prompt. *Mitigation*: invoke `scripts/validate_skills.py`, `pre-commit`,
  and Vale directly when that happens.

## Open questions

None blocking. Two shaping decisions were settled during pre-analysis and are recorded
above rather than deferred: the skill carries a `plan` operation (no mechanical `apply`),
and runtime behaviour stays advisory/`[runtime-verify]` and never hard-fails.

## Dispatch log

2026-08-01 P1 dispatched to `nolte-shared:spec` — settled. §Open Questions in `en.md` + `de.md`
now records the capability as settled 2026-08-01 with the artefact names, the six checks, and
the static-vs-runtime carve-out; `spec/README.md` row refreshed to 2026-08-01. **Scope
correction beyond the brief:** the section's framing sentence still asserted the audit shape
was "the one genuinely open remainder", which the settlement falsifies — it was rewritten in
both languages rather than left contradicting the bullet below it. Translation drift check
passed (15 headings, 5 Open-Question bullets, 11 checkboxes in both languages); Vale 3.15.2
clean on `en.md`. Commits 40b90de, 4ed7bea.

