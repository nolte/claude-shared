---
review-type: skill-review
target: "skills/pull-request-create/SKILL.md"
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

# Skill Review: pull-request-create

## Scope

Target: `skills/pull-request-create/` (SKILL.md, references/{open-pr-slot,class-sweep,gotchas}.md, examples/01–03).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — `skills-ref` isn't provisioned in this repository; `scripts/validate_skills.py` (the repository's frontmatter, body-size, and asset validator behind `task test`, CLAUDE.md §"Command entry points") ran in its place.
Narrowing: the changes of `feat/serial-pr-flow` (`origin/develop...386a9a51`) plus the full validator run and a load-trigger and broken-reference scan over every asset; unchanged sections were judged only through the validator.
Explicitly out of scope: runtime behavior of the skill, Vale/markdown style (handled by `task lint`), dispatched agents beyond confirming the orchestration direction.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 0
- Info: 1

Go/no-go: CONDITIONAL — body back under the 4,500-token warning band
Next concrete action: move the rationale and the audit-remediation rules into references/

## Findings

### Critical

- none

### Warning

- [ ] [skill-management.body-token-approaching] Validator: body ~4,919 tokens, inside the warning band after the slot precondition was added.
      Where: skills/pull-request-create/SKILL.md (whole body).
      Fix: move the skill-vs-agent rationale and the audit-remediation lines plus checklist into references/ with load triggers.
      Verify: python3 scripts/validate_skills.py reports no body-token finding for this skill.

### Suggestion

- none

### Info

- [ ] [skill-review.frontmatter] `--orchestrated` is declared only in the precondition bullet and references/open-pr-slot.md, not in an Arguments section; the skill has no Arguments section at all.
      Where: skills/pull-request-create/SKILL.md:46.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log
