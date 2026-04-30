---
review-type: skill-review
target: "skills/github-issue-templates-apply/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "38f4fc010a020aac3da9ae8465d49889d5146f39"
  - slug: skill-vs-agent
    revision: "0e3b6f9fc64bbfd97c74c2575d25fcfcae5598d6"
  - slug: review-plan
    revision: "0e3b6f9fc64bbfd97c74c2575d25fcfcae5598d6"
  - slug: skill-review
    revision: "38f4fc010a020aac3da9ae8465d49889d5146f39"
repo-revision: "38f4fc010a020aac3da9ae8465d49889d5146f39"
created: "2026-04-30"
status: open
---

# Skill Review: github-issue-templates-apply

## Scope

Target: `skills/github-issue-templates-apply/` — `SKILL.md` (147 lines), referenced assets `templates/bug_report.template.yml`, `templates/feature_request.template.yml`, `templates/config.template.yml`, `references/project-type-fields.md`. The skill and its parent spec `spec/project/github-issue-templates/` are still untracked in the working tree, so the `repo-revision` above pins HEAD; the reviewed files themselves are not yet committed.

This run **supersedes** the previous plan at the same path. The previous plan (status `open`, 0B / 0W / 1S / 3I) was created before the Spec gained the bug-vs-feature strictness profile and before the skill grew the per-template strictness rule, the self-validation pass in Operation 3, the strictness-drift class in Operation 6, the strictness Hard rule, and the default-branch Gotcha. Findings below have been re-evaluated against the current sources; the spec changes did not introduce or resolve any finding.

Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — `skills-ref` (Anthropic's canonical external skill-structure validator) is not provisioned in this repository and no alternative validator is declared in repo tooling; per `skill-review` §"Checks derived from external skill-structure validation" MAY suppress, the spec-derived checks below stand in until a validator is provisioned. Re-run this review once a validator is wired up.
Narrowing: none.
Dispatched-agent companion review: not applicable — the skill dispatches another *skill* (`audience-identify`), not an agent; `skill-vs-agent` §Hybrid pattern explicitly allows skill-to-skill calls in the same thread, and `agent-review` is not triggered.
Explicitly out of scope: runtime behavior of the skill (no live execution per `skill-review` §Non-Goals), Vale / markdown style (handled by `task lint`), the parent spec `spec/project/github-issue-templates/` (its own readiness check is `spec-readiness-reviewer`, not this review type).

## Summary

- BLOCKER: 0
- WARNING: 0
- SUGGESTION: 1
- INFO: 3

Go/no-go: PASS — the skill conforms to every MUST in `skill-management`, `skill-vs-agent`, and `review-plan` that this review type checks, including the new per-template strictness contract added in the latest spec revision. The single SUGGESTION and the three INFOs are non-blocking and may be addressed in a follow-up commit or deferred to issues.
Next concrete action: author may either (a) accept the SUGGESTION and add a one-line "Plan-validate-execute" / "Validation loop" naming to Operations, or (b) close this plan as-is with `→ deferred:` annotations on the three INFOs.

## Findings

### SUGGESTION

- [ ] [skill-management.authoring-quality.plan-validate-execute] Operations 3 (self-validation pass on the working set), 4 (Disclose the plan and confirm), and 5 (Apply, atomic with rollback) collectively implement two stacked validation loops — a pre-disclose check inside the skill and a user-confirm gate before any write — but the SKILL.md never names the pattern; `skill-management` §"Authoring quality" MAY recommends a "Validation loop" or "Plan-validate-execute" subsection for skills that perform batch or destructive operations, and naming it would make the pattern recognisable to future reviewers.
      Where: `skills/github-issue-templates-apply/SKILL.md` "## Operations" header (around line 32) or as a prelude to Operation 4.
      Fix: add a one-line note at the top of the "## Operations" block ("Operations 3–5 form a stacked Plan-validate-execute cycle: the skill self-validates the working set, surfaces it for user confirmation, then writes atomically with rollback on partial failure.") or a dedicated `### Plan-validate-execute pattern` subsection.
      Verify: `grep -i 'plan-validate-execute\|validation loop' skills/github-issue-templates-apply/SKILL.md` returns at least one hit.

### INFO

- [ ] [skill-review.external-validator] External skill-structure validator (`skills-ref`) is not provisioned in this repository, so the spec's MUST-run external-validator check was suppressed via the `## Scope` override clause; this is allowed by `skill-review` §"Checks derived from external skill-structure validation" MAY but worth flagging so the project tracks the gap.
      Where: this plan's `## Scope` "Validator: override — …" line; `skill-review` MUST §"Checks derived from external skill-structure validation".
      Fix: n/a (observation) — when `skills-ref` (or an equivalent validator declared in repo tooling) becomes available, re-run `skill-review run github-issue-templates-apply` so the structural checks run against the binary, not just the spec-derived approximation.
      Verify: n/a (observation).
- [ ] [skill-vs-agent.rationale.counter-dimension] The rationale section names exactly one counter-dimension (specialisation — a narrow YAML-form-generator agent could sharpen Issue-Forms-syntax output); `skill-vs-agent` §"Rationale documentation" SHOULD asks for at least one counter-dimension, so the bar is met. Parallelism would be a second plausible counter-dimension if multi-repo batch runs ever become a use case (an agent could fan out across multiple repos in parallel), but the current single-repo contract makes that hypothetical, not load-bearing.
      Where: `skills/github-issue-templates-apply/SKILL.md` line 16 (counter-dimension bullet under "## Why this is a skill, not an agent").
      Fix: n/a (observation) — only reconsider if the skill grows a multi-repo batch mode, at which point the rationale should be revisited.
      Verify: n/a (observation).
- [ ] [skill-management.authoring-quality.references-size] `references/project-type-fields.md` is 349 lines and bundles six project-type sections in a single file. There is no hard cap on `references/` files (only `SKILL.md` carries the 500-line / 5,000-token cap), and the load-trigger phrase in `SKILL.md` line 62 is concrete enough that progressive disclosure works. Splitting into `references/<project-type>-fields.md` per type plus a `references/README.md` index would let the skill load only the matching bundle, reducing unnecessary read volume on each invocation.
      Where: `skills/github-issue-templates-apply/references/project-type-fields.md` (entire file).
      Fix: n/a (observation) — defer until usage shows the unified file is too coarse; the current shape is a sensible v1 starting point.
      Verify: n/a (observation).

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-04-30 — n/a — plan superseded after spec/skill update (added per-template strictness profile, self-validation pass, strictness-drift class, default-branch Gotcha) — verified: re-read of SKILL.md line counts, references intact, all MUSTs from updated spec satisfied.
