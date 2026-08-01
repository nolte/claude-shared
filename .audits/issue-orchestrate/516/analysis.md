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

2026-08-01 P2 dispatched to `nolte-claude-dev:claude-plugin-developer` — delivered
`plugins/nolte-engineering/agents/error-tracking-audit-scanner.md` (draft-and-return; the
subagent cannot reach worktree paths, so the orchestrator wrote the file). **Refutation
returned and verified — blocking, accepted:** the brief's "keep the description at sibling
density" premise was wrong. `check_agent_description_budget` freezes
`plugins/nolte-engineering/agents` at baseline 18535 with a 21315 ceiling; the 36 existing
agents already consume 21156, leaving **159 chars**. Even at 713 chars — below the 748-char
sibling — the new agent pushed the aggregate to 21869 and tripped a `Critical`. Reproduced
independently with `python3 scripts/validate_skills.py`. **Operator decision 2026-08-01:**
re-baseline to 21869 with a recorded rationale, the remedy the gate's own message names; the
gate guards regression, not deliberate growth, and platform-wide agent-description weight is
~8.6k est. tokens against the ~15k routing budget. The "post-remediation-baseline artefact"
the message also names no longer exists (`.audits/` emptied 2026-07-24), so the
`AGENT_DESC_BASELINE_CHARS` comment is the sole rationale record. Second, non-blocking
refutation accepted: three classifications were deliberately left non-binary by the scanner
(default-PII unset vs. explicit false; DSN build-baked vs. hardcoded literal; a `release`
constant that never moves) because the severity split is the skill's triage call, not the
detector's — folded into the P3 brief. Two checks were added beyond the brief: the CSP
`connect-src` ingest origin (advisory; a restrictive policy silently blocks every event POST
even with perfect SDK wiring) and an error-vs-traces sample-rate carve-out. Validator exit 0,
no findings on the new agent. Commit 95693e9.

2026-08-01 P3 dispatched to `nolte-claude-dev:claude-plugin-developer` — delivered
`SKILL.md` plus `references/{check-policy,report-shape}.md`. **Three refutations returned,
all accepted:** (1) the brief asked which of the checks are mandatory versus advisory, but
`en.md:41–53` states every tool-contract item as a MUST while the only SHOULDs (`:50`
explicit capture, `:54` source maps) already sit in the scanner's separate Advisory block —
so the split runs along the scanner's own section boundary and no intra-contract split was
manufactured; (2) the body did not fit the 5,000-token cap at the briefed depth (~4,957 est.
tokens), so the mechanical per-check violation definitions and the report template moved into
`references/` with explicit load triggers, keeping every decision the skill owns inline;
(3) `dont_use_when` needed a fifth neighbour the brief omitted — `api-error-check`, since the
spec's own delimitation (`en.md:14`) names `api-error-handling` and the closest false trigger
("check our error handling") would otherwise be unrouted. Validator exit 0. Commit 6878340.

2026-08-01 P6 (generalist calibration against `~/repos/github/kamerplanter`) — all six checks
resolve to a finding with `file:line` across all five components, and the three anti-naive
detection rules each fire on their intended target. The two-entrypoints-in-one-root rule also
caught `src/backend/app/tasks/__init__.py:20` (worker) as a second component beside
`main.py:38`. **One defect found:** the scanner's Phase 1 treats a package-name occurrence in
a manifest as a declaration. In `src/knowledge-service/pyproject.toml` the only "sentry"
occurrence is a `[[tool.mypy.overrides]]` entry (`:64`) while the real declaration is in
`requirements.txt:11` — a name-match scanner would report the SDK as declared *and* miss the
actual declaration. Fix folded into the P2 artefact together with the P4/P5 review outcomes.

2026-08-01 P4 (`nolte-claude-dev:agent-review` lane, adversarial) — 1 Critical, 7 Warnings,
4 Suggestions; verdict "ship with fixes". The Critical and three Warnings share one root: the
pair was drafted in two dispatches, so the skill's `check-policy.md` defined FAIL states the
scanner never detects (dev/local path pinning a production value — the spec's only statically
decidable lifecycle violation) or cannot express (a late init, a non-protocol client, two of
three no-DSN failure modes). Three honesty defects also confirmed: a scope leak labelling DSN
classes "conformant" against its own hard rule; a claim that the tool grant prevents a probe
event when `Bash` can reach the network; and a CSP check declared `[static]` that is
undecidable exactly when the DSN is conformant. All fixed in 8c64aef.

2026-08-01 P5 (`nolte-claude-dev:skill-review` lane, adversarial) — 2 Criticals, 10 Warnings,
5 Suggestions; verdict "block". Both Criticals verified against source before acting.
**C1:** `implementation-plan-author.md:38,244` carries a closed three-source list and a hard
rule rejecting anything else, so the `plan` operation dispatched into a refusal. **Operator
decision:** extend it with a fourth sanctioned source, body-only, so the budget re-baselined
under P2 holds — confirmed unchanged at 21869. **C2:** the skill demoted a MUST for browsers
while raising an unwritten requirement to Critical server-side. `en.md:42` mandates only
injection via environment/deployment configuration and no literal in the source tree — a
`VITE_*` build variable satisfies both, and the stage-portability rationale appears nowhere in
the spec. **Operator decision:** uniform Warning for build-baked, spec left unchanged, rather
than inventing a portfolio-wide requirement. The review also refuted one premise of my brief:
`see_also` bidirectionality is not a spec MUST (`skill-agent-catalog` requires resolvability;
the "Referenced by" inversion is the generator's SHOULD, existing precisely to surface
one-directional links). All findings fixed in 8c64aef; the fixes pushed the skill body over
the 5,000-token cap, so the runtime-verify enumeration and the gotchas moved into
`references/` with load triggers, leaving the body at ~4762 tokens. Validator exit 0,
pre-commit green, Vale clean.

