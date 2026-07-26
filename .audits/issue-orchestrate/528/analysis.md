---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: 528
classification: "spec-change"
secondary-classes: []
route: "direct"
status: draft
created: "2026-07-26"
---

# Issue Orchestration — Pre-analysis

Run-scoped artifact. Committed on `feat/dispatch-brief-rule`, then removed with a
fix-forward `git rm` before the PR merges, per `spec/project/issue-orchestration/`
§Pre-analysis artifact lifecycle.

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #528 — spec(claude): make "the specialist may refute the brief" a portfolio-wide dispatch rule, not an E2E-local one
- **URL**: https://github.com/nolte/claude-shared/issues/528
- **Labels**: none
- **Linked items**: none (no linked PRs; derived from `nolte/kamerplanter#768`, filed here as #514 — closed via PR #527)
- **Prior art checked**: `spec/project/e2e-failure-diagnosis/` §E (line 96) + §Binding (line 141) already carry the E2E-scoped rule; `spec/claude/` cross-cutting specs surveyed (`agent-management`, `skill-management`, `skill-vs-agent`, `research-triangulate`) — none owns brief composition. One existing reference found: `plugins/nolte-engineering/agents/gdpr-data-protection-reviewer.md` uses the confirm/refute framing. No open PR addresses this.

## Trust boundary

Issue author `nolte` resolved as repository owner (admin + maintain + push) — a
trusted author per `spec/claude/trusted-author-injection-guard/`. The issue's
numbered requested changes are executable instructions, not merely quoted data.

## Requirements gate

No requirement artefact under `project/requirements/`. **Operator override recorded**
(scope-confirmation gate, 2026-07-26): the issue is fully specified — numbered
requested changes #1–#5, explicit acceptance criteria, and campaign evidence — so
`U_gate` is met by the issue itself; `requirements-elicit` skipped by operator
decision.

## Classification

- **Primary class**: spec-change
- **Secondary class(es)**: none
- **Rationale**: Creates a new cross-cutting spec under `spec/claude/` and edits an existing spec plus the skills bound to it; no code behaviour changes.

## Scope

- **In scope**:
  1. A new cross-cutting spec `spec/claude/dispatch-brief/` (EN canonical + DE translation) stating the refutation rule as a checkable requirement, and specifying the shape of a valid refutation (evidence that contradicts the brief + what the specialist did instead: nothing, a narrower fix, or a different fix).
  2. Retargeting `spec/project/e2e-failure-diagnosis/` (EN + DE) so §E and §Binding cross-reference the new spec instead of carrying their own copy of the rule.
  3. Referencing the new rule from the dispatching skills that assert a hypothesis in their briefs.
  4. Spec index regeneration if the repo maintains one; EN + DE parity; Vale-clean EN.
- **Out of scope**: Changing the *content* of any dispatch brief at runtime; authoring new dispatching skills; the `api-documentation-audit` capability named in the issue has no dispatching skill in this repo (only the `api-documentation-scanner` agent) — recorded as a no-op target, not wired.

## Route

- **Decision**: direct
- **Rationale**: One coherent outcome (relocate a rule to a cross-cutting home + wire the references), a single PR strand, no new or retargeted roadmap item. Confirmed by operator at the scope gate.

## Work packages

### P1 — Author `spec/claude/dispatch-brief/` (EN canonical + DE)

- **Problem statement**: The refutation rule lives only in a domain spec. Author a new cross-cutting spec that owns it portfolio-wide, stated as a reviewer-checkable requirement.
- **Acceptance criteria**:
  - `spec/claude/dispatch-brief/en.md` and `de.md` exist, structurally parallel, with the standard spec sections (Context, Goals, Non-Goals, Requirements, Acceptance Criteria).
  - The rule is stated as a MUST a reviewer can check against an actual brief: a brief that asserts a cause, a mechanism, or a remediation shape MUST also state that the specialist may refute it, and MUST frame a refutation as a valid, expected deliverable rather than a failure to complete the task.
  - The shape of a valid refutation is specified: the evidence that contradicts the brief (a `file:line` or a command whose output settles it) **and** what the specialist did instead (nothing / a narrower fix / a different fix). A bare "I disagree" is explicitly non-conformant.
  - EN is Vale-clean; DE mirrors the MUST-keywords.
  - The spec index (if maintained) lists the new spec.
- **Touched files / artifacts**: `spec/claude/dispatch-brief/en.md`, `spec/claude/dispatch-brief/de.md`, spec index if present.
- **Specialist**: `nolte-shared:spec` (skill; owns spec authoring, translation, indexing — invoked in-thread targeting worktree paths).
- **Depends on**: none

### P2 — Retarget `spec/project/e2e-failure-diagnosis/` to cross-reference

- **Problem statement**: The E2E spec must point at the new portfolio-wide home instead of duplicating the rule (requested change #4).
- **Acceptance criteria**:
  - §E (en.md line ~96 / de.md equivalent) and §Binding (line ~141 / equivalent) reference `spec/claude/dispatch-brief/` as the authoritative owner and no longer restate the rule's body.
  - The E2E spec retains only its E2E-scoped application (dispatch briefs in parallel multi-channel triage carry the clause), delegating the general rule.
  - EN + DE parity preserved; the "issue comment §H, sited here as the authoritative rule" framing is corrected to point outward.
- **Touched files / artifacts**: `spec/project/e2e-failure-diagnosis/en.md`, `spec/project/e2e-failure-diagnosis/de.md`.
- **Specialist**: `nolte-shared:spec`.
- **Depends on**: P1

### P3 — Wire the rule into the dispatching skills

- **Problem statement**: The rule is only worth having if the brief-composing skills reference it (requested change #5).
- **Acceptance criteria**:
  - Each dispatching skill that asserts a hypothesis in its brief carries a reference to `spec/claude/dispatch-brief/` in the passage where it composes a specialist dispatch.
  - Proposed set (refine against the stated-hypothesis criterion): `skills/issue-orchestrate` and `skills/workflow-health-triage` (nolte-shared, both assert a decomposition/classification hypothesis — strong), and `plugins/nolte-engineering/skills/{source-code-review,dependency-audit,observability-audit,test-cycle-orchestrate}` (named in the issue; test-cycle-orchestrate is the tier-reviewer dispatcher).
  - `api-documentation-audit` is recorded as having no dispatching skill (only `api-documentation-scanner` agent) — not wired.
- **Touched files / artifacts**: the six `SKILL.md` bodies above.
- **Specialist**: no worktree-reachable specialist — `claude-plugin-developer` is an agent and background subagents can't reach this worktree's path or run git (per portfolio operational note); handled as **generalist remediation** (light, identical cross-reference edits), with the note carried into the PR.
- **Depends on**: P1

## Dependency ordering

P1 → P2 ; P1 → P3  (P2 and P3 both gate on P1; independent of each other.)

## Risks

- **Vale on EN spec prose** — Microsoft-style rules (mandatory contractions, unspaced em-dashes not on code/bold, punctuation-in-quotes) apply to `spec/**/en.md`. Mitigation: author EN Vale-aware; run the CI-pinned Vale 3.15.2 locally before PR.
- **EN/DE drift** — parity is an AC. Mitigation: `spec` skill authors both and its translation sync check runs.
- **Wiring-set judgment** — which skills "assert a hypothesis" is a judgment; over-wiring (adding the clause to a pure scan-scope dispatch) is low-cost, under-wiring misses the point. Mitigation: the proposed set is recorded; operator may trim/extend at the P3 gate. See open question 1.
- **No security-sensitive paths touched** — `code-security-reviewer` / `security-review` not required for this change.

## Open questions

1. **Wiring set precision** — should P3 wire all six proposed skills, or only the two strong-hypothesis dispatchers (`issue-orchestrate`, `workflow-health-triage`) plus the issue-named engineering trio, treating `test-cycle-orchestrate` as covered by the spec binding alone? Default: wire all six.
2. **Dedicated-spec size** — the new spec is small (one rule + refutation shape). Confirmed proportionate as a standalone spec at the scope gate; no action unless the operator prefers folding it back.

## Dispatch log

<!-- Appended during operation 5. -->
