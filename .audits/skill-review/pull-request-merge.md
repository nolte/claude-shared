---
review-type: skill-review
target: "skills/pull-request-merge/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "4ceb6872"
  - slug: skill-vs-agent
    revision: "66d65137"
  - slug: review-plan
    revision: "7be3b552"
  - slug: skill-review
    revision: "7be3b552"
repo-revision: "386a9a51"
created: "2026-11-09"
status: open
---

# Skill Review: pull-request-merge

## Scope

Target: `skills/pull-request-merge/` (SKILL.md, references/{branch-cleanup,automerge-verification,wait-mode}.md).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — `skills-ref` isn't provisioned in this repository; `scripts/validate_skills.py` (the repository's frontmatter, body-size, and asset validator behind `task test`, CLAUDE.md §"Command entry points") ran in its place.
Narrowing: the changes of `feat/serial-pr-flow` (`origin/develop...386a9a51`) plus the full validator run and a load-trigger and broken-reference scan over every asset; unchanged sections were judged only through the validator.
Explicitly out of scope: runtime behavior of the skill, Vale/markdown style (handled by `task lint`), dispatched agents beyond confirming the orchestration direction.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 0
- Info: 0

Go/no-go: CONDITIONAL — body back under the 4,500-token warning band
Next concrete action: move the multi-PR section into references/

## Findings

### Critical

- none

### Warning

- [ ] [skill-management.body-token-approaching] Validator: body ~4,769 tokens, inside the warning band.
      Where: skills/pull-request-merge/SKILL.md (whole body).
      Fix: move the one-open-PR detail into references/one-open-pr.md, condense step 7's cause list into references/automerge-verification.md, and shorten the rationale pointer.
      Verify: python3 scripts/validate_skills.py reports no body-token finding for this skill.

### Suggestion

- none

### Info

- none

## Processing log
