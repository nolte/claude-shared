# Group pre-analysis: 2026-11-17-red-check-handling

- Repository: nolte/claude-shared, develop at worktree creation
- Source: partition .audits/issue-backlog-partition/2026-11-17.md (operator-approved), lane; ordered after 2026-11-17-merge-review-gate (merged #783)
- Tier: 2

## Scope of this analysis

Question: what has to change so the delivery train stops on a red `develop` and the triage classifies a failure that recurs with the same message as a defect, with side-effect-free diagnostics?

Logical change: **The delivery train stops on a red develop and the triage classifies a failure that recurs with the same message as a defect, using side-effect-free diagnostics.**

## Members

| Issue | Class | Predicate | Evidence (re-checked against the live issues) |
|---|---|---|---|
| #776 | feature-request | thematic coupling | `skills/workflow-health-triage/SKILL.md:74` classifies "re-run of the same headSha would produce green" as `flake`; no recurrence, side-effect-free-diagnostics or first-red-vs-last-green rule (`grep` over the skill and `spec/project/workflow-health/en.md`) |
| #773 | feature-request | thematic coupling + dependency chain | no skill reads the latest `develop` runs before a lane or merge (`git grep "gh run list --branch develop"` → 0 hits in skills/ and spec/); its pre-flight hands a red `develop` to the triage #776 changes |

Both authors nolte (trusted), no comments, no linked PRs, both bounded. Order: #776 → #773.

## Mode decision

Mode A: #773's hand-off relies on #776's classification; neither is removable alone without weakening the other.

## Structural finding

Symptom cluster (confirms the partition): one root failure (nolte/kamerplanter-appliance#39, a red vm-test on develop treated as flake and as "not this PR"), two blind spots — the triage's flake default for recurring failures, and the train never looking at develop's own runs.

## Plan approval

Covered by the operator's standing authorisation of 2026-11-17 for the approved partition outcomes (recorded in the partition artifact); `authorised_by: 2026-11-17-red-check-handling/plan-approval`.

## Completeness matrix

| Member | Skills (source) | Spec | Tests | Docs | Config / workflows | Generated index |
|---|---|---|---|---|---|---|
| #776 | `skills/workflow-health-triage/SKILL.md` classification table and dispatch brief: recurring identical failure ⇒ `defect` until measured otherwise; side-effect-free diagnostics in the brief; compare first red with last green; check: `validate_skills.py` | `spec/project/workflow-health/` §Flake handling / §Triage before remediation (EN+DE): same three rules; check: section refs + Vale | not applicable — instruction text; no unit-testable code | not applicable | not applicable | not applicable — description unchanged unless needed; if changed, `task docs` |
| #773 | shared pre-flight reference (where it lives decided in the run) used by `issue-backlog-partition` (dispatch), `backlog-delivery-orchestrate` (before each promotion), `pull-request-merge` (step 1): latest run of every workflow on develop, red ⇒ stop and hand to `workflow-health-triage`, override only recorded in the checkpoint; check: `validate_skills.py` (pull-request-merge ~4471 tokens: net ≤ 0 in its body) | `spec/project/pull-request-workflow/` §Serial pull-request flow (EN+DE, MUST + AC); check: section refs + Vale | not applicable | not applicable | not applicable | catalog if a description changes; check: `task docs` |

## Risks

- `pull-request-merge` body near the 4,500 warning: the pre-flight goes into a reference with a pointer.
- A develop workflow that is red for an unrelated, known reason would stop every lane: the rule needs an explicit, recorded override path, not a silent skip.

## Open questions for the operator

none

## Member results

| Member | Result | Verification (actual output) |
|---|---|---|

## Deviations

none yet

## Requirement coverage

not applicable — symptom cluster

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|
