---
review-type: skill-review
target: "skills/issue-orchestrate/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "66d6513791380914c73b78c360b5740c29ef13ba"
  - slug: skill-vs-agent
    revision: "66d6513791380914c73b78c360b5740c29ef13ba"
  - slug: review-plan
    revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
  - slug: skill-review
    revision: "66d6513791380914c73b78c360b5740c29ef13ba"
repo-revision: "3ba248e5b062fad4670b4f8470708c03784ecf43"
created: "2026-07-25"
status: in-progress
---

# Skill Review: issue-orchestrate

## Scope

Target: `skills/issue-orchestrate/` (full review; frontmatter, body, and every referenced supporting file).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions in frontmatter).
Validator: `scripts/validate_skills.py` (the repository's `skills-ref` stop-gap per `skill-review` §External skill-structure validation), run via `task test` at repo revision 3ba248e5: no Critical/Warning validator findings for this skill beyond those listed below; token measurements below use the validator's body-only 4-char heuristic as the authoritative reading where a reviewer estimate differed.
Context: 2026-Q3 coverage batch (issue #492, finding `skill-review.coverage-gap`) — first recorded review for this skill since spec adoption. Review executed as a read-only checklist pass (frontmatter limits, third-person description with what+when triggers, rationale section with counter-dimension, spec anchor, referenced-asset existence and load triggers, reference depth, ToC on >100-line supporting files, path hygiene, language, duplicate-capability grep, standing-instructions phrasing, Gotchas, evaluation scenarios, MCP tool naming).
Explicitly out of scope: runtime behavior, Vale/markdown style (own tooling).

## Summary

- Critical: 0
- Warning: 2 (2 closed)
- Suggestion: 0
- Info: 0

Go/no-go: PASS — no open Critical; every Critical/actionable Warning fixed in this batch, 0 item(s) deferred with annotation.

## Findings

### Critical

<!-- none -->

### Warning

- [x] [skill-review.body-size] Reviewer estimated the body over the ~5,000-token budget; the authoritative validator measured 4,986 (approaching, not over) — downgraded per §Scope note.
      Resolution: Gotchas bullet list extracted to references/gotchas.md with a conditional load trigger; validator now ~4,753 (fixed in this batch).

- [x] [skill-review.duplicate] Operation 3 decomposes inline while the implementation-plan-author agent exists for exactly that work.
      Resolution: operation 3 now prefers dispatching implementation-plan-author when nolte-engineering is installed, inline path kept as fallback (fixed in this batch).

### Suggestion

<!-- none -->

### Info

<!-- none -->
