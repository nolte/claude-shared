---
name: spec-drift-audit
description: Audits every spec under spec/<topic>/<slug>/ against the repository implementation (source code, config, workflows, docs) and produces a traceable audit artifact per spec/project/spec-drift-audit/. Invoke when the user asks to "run the quarterly spec-drift audit", "check spec versus implementation", "spec drift reconciliation", "audit all specs against the repo", "find spec vs code drift", "open the next quarterly audit", or when a spec changes and requires a matching partial audit. Also handles equivalent German-language requests. Do NOT use for continuous CI health checks (use workflow-health-triage), single-spec readiness review (use spec-readiness-reviewer agent), or feature-level code drift on new features (use feature-consistency-reviewer agent within feature-decompose scope). Supports resume on re-invocation per `spec/claude/resumable-work/`.
tags: [audit]
phase: review
summary: "Audits every spec against the repository implementation and produces a traceable spec-drift audit artifact."
summary_de: "Auditiert jede Spec gegen die Repo-Implementierung und erzeugt ein traceable Spec-Drift-Audit-Artefakt."
use_when:
  - "you want to run the quarterly spec-drift audit"
  - "you want to reconcile a spec against the actual implementation in the code"
  - "you want to open a partial audit after a spec change"
dont_use_when:
  - situation: "You want continuous CI health checks rather than spec drift"
    alternative: workflow-health-triage
  - situation: "You want a single-spec readiness audit before promotion"
    alternative: spec-readiness-reviewer
  - situation: "You want feature-level drift on new features"
    alternative: feature-consistency-reviewer
see_also:
  - spec-readiness-reviewer
  - feature-consistency-reviewer
  - workflow-health-triage
resumable: true
---

# Spec Drift Audit

Operationalises `spec/project/spec-drift-audit/<canonical_language>.md` — reconciles every in-scope spec's Requirements and Acceptance Criteria against the actual repository state, persists the result as a dated artifact, and drives findings to a documented decision. The audit artifact is the deliverable; this skill is the procedure that creates, updates, and closes it.

## Why this is a skill, not an agent

- **Mid-flow interactivity** — the user decides per finding: adjust the implementation, adjust the spec, or flag as an Open Question. An agent's fire-and-forget contract loses that deliberation loop.
- **Persistent on-disk output** — the audit artifact under `docs/audits/YYYY-Q<n>.md` (or a GitHub issue) must survive past the current turn and be worked off incrementally; skills own persistent artifacts, agents return ephemeral reports.
- **Orchestration role** — the audit dispatches `project-structure-apply` and `vocab-drift-audit` as partial auditors in the same session; the skill-orchestrates-agent-executes pattern defaults the orchestrator to skill form.
- Counter-dimension considered: *context-window load* from reading all specs plus their implementation surfaces could bias toward an agent, but the audit is inherently interactive and scoped per cycle — the user controls which specs are in scope and confirms each finding disposition. Inline execution in the skill form wins.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "führe den quartalsweisen Spec-Drift-Audit durch"
- "Spec gegen Implementierung prüfen"
- "Spec-Drift-Abstimmung"
- "alle Specs gegen das Repo auditieren"
- "nächsten Quartals-Audit öffnen"
- "Spec-Änderung erfordert Teil-Audit"

## Preconditions

Before any operation, verify:

1. `spec/.spec-config.yml` is present — read it to determine `canonical_language` (fall back to `en`).
2. `spec/project/spec-drift-audit/<canonical_language>.md` is present — this is the governing spec; stop if missing.
3. `docs/audits/` exists or can be created (check `git ls-files docs/audits/.gitkeep`); create `docs/audits/.gitkeep` if the folder is absent.

## Operations

### 1. `audit` — produce the audit artifact

Interactive. Confirm scope and trigger with the user before proceeding.

1. **Determine trigger and scope.** Ask (or infer from the message): quarterly full-scope, or thematic partial triggered by a specific spec change or new skill/agent? Record the trigger. For thematic audits, confirm which spec topic is in scope.
2. **Determine the Git revision.** Run `git rev-parse HEAD`; record it as `repo-revision`.
3. **Collect in-scope specs.** Walk `spec/<topic>/<slug>/<canonical_language>.md` for every file whose `## Requirements` or `## Acceptance Criteria` section is non-empty. `Status: draft` specs are included. For a thematic audit, narrow to the declared topic area — record the narrowing.
4. **Dispatch partial auditors.** For the implementation surfaces covered by existing skills, delegate and capture their output:
   - Run `project-structure-apply` (audit mode only) to check `.github/`, `Taskfile.yml`, MkDocs, Renovate, and Probot alignment.
   - Run `vocab-drift-audit` to check Vale vocabulary against the pinned upstream release.
   - Run `task lint` and record the result.
   Record each tool's name and version (or git SHA) in the artifact's `tools-used` list.
5. **Per-criterion check.** For each remaining spec criterion not covered by a dispatched tool, evaluate against the implementation: produce one of `pass`, `fail`, `blocked` (tooling missing), or `not-applicable` (with reason). Record the result.
6. **Draft the artifact.** Read `templates/audit.template.md` for the Markdown template. Fill every frontmatter field. List all findings with `fail` or `blocked` status in `## Findings`. Leave `## Decisions` empty at creation.
7. **Write the artifact** to `docs/audits/<YYYY>-Q<n>.md` (or `docs/audits/<YYYY>-Q<n>-<topic>.md` for thematic audits). Confirm the path with the user.
8. **Offer to stage and commit.** Show the artifact path. Do not commit without explicit user confirmation.

Read `examples/01-quarterly-audit.md` when running a full-scope quarterly audit to see a realistic walkthrough.
Read `examples/02-spec-change-trigger.md` when running a thematic partial audit triggered by a spec update.

### 2. `update` — record decisions on findings

When the user reports decisions for one or more findings:

1. **Read** the current audit artifact from `docs/audits/`.
2. **Verify** each claimed closure: re-read the relevant spec criterion and the referenced implementation file. Do not accept "done" without spot-checking.
3. **Record the decision** per finding: `adjust-impl`, `adjust-spec`, or `open-question`. Update the `## Decisions` section.
4. **Append one log line** to `## Processing log` per decision: `YYYY-MM-DD — <finding-id> — <decision> — verified: <method>`.
5. **Flip `status`** in artifact frontmatter to `in-progress` on first decision.
6. **Show the diff.** Do not commit automatically.

Read `examples/03-finding-resolution.md` when working off findings via update and close operations.

### 3. `close` — seal the audit cycle

1. **Read** the current audit artifact.
2. **Refuse if any `fail` finding lacks a decision.** `blocked` findings may be closed with an `open-question` decision plus a tracking issue URL.
3. **Flip `status`** in frontmatter to `closed`. Record the closing date.
4. **Compose the commit message**: `chore(audit): close <YYYY>-Q<n> spec-drift audit — <F> findings, <D> decisions` in the subject; body lists open-question URLs and `repo-revision`.
5. **Run the commit only with explicit user confirmation.** Show the message first.

## Examples

- Read `examples/01-quarterly-audit.md` for a full-scope quarterly audit with multiple findings and mixed decisions.
- Read `examples/02-spec-change-trigger.md` for a thematic partial audit triggered by a specific spec update.
- Read `examples/03-finding-resolution.md` for working off findings with the `update` and `close` operations.

## Gotchas

- **`spec/.spec-config.yml` must be read first.** The canonical language for spec paths depends on `canonical_language` in that config. Defaulting to `en` without reading the config silently routes to the wrong language in repos with a different canonical.
- **`Status: draft` specs are in scope.** The governing spec explicitly includes draft specs in the audit perimeter. Do not skip them.
- **Partial auditors only cover their slice.** `project-structure-apply` and `vocab-drift-audit` are delegated tools but each covers only one surface. Remaining spec criteria need direct per-criterion evaluation — never assume "dispatched means done".
- **Artifact location is repository-consistent.** If `docs/audits/` already contains prior artifacts, match the existing naming convention rather than inventing a new one. Check for prior artifacts before writing.
- **Calendar quarter, not rolling.** Q1 = Jan–Mar, Q2 = Apr–Jun, Q3 = Jul–Sep, Q4 = Oct–Dec. A `2026-Q2` audit covers the April–June window regardless of the actual date within the quarter.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/spec-drift-audit/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Every `fail` finding needs a documented decision before `close`.** Silent deferrals violate the governing spec and the audit history requirement.
- **Record the Git revision.** Every artifact must carry `repo-revision` so the audit can be reproduced. `unknown` is acceptable for detached HEADs; omission is not.
- **No tool without a version.** Every dispatched tool (skill, CLI, action) must appear in `tools-used` with its version or SHA.
- **No invented pass/fail.** If a criterion can't be evaluated (tooling absent, access missing), mark `blocked` — never guess `pass`.
- **One artifact per audit cycle.** A re-run for the same quarter-scope supersedes; never merge two partial audits into a single file retroactively.
- **English artifact structure, user language in prose.** Section headings (`## Findings`, `## Decisions`, etc.) stay in English for grepping and downstream tooling; finding prose follows the user's language.

## Multi-model testing

Examples and operations in this skill are verified on Claude Sonnet 4.6 as the default model; spot-checked on Haiku 4.5 for lightweight partial audits; Opus 4.7 is appropriate for full-scope audits requiring deeper cross-spec reasoning. The skill has no model-specific assumptions beyond standard tool-call semantics.
