---
review-type: skill-review
target: "skills/pull-request-runner-sweep/SKILL.md"
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

# Skill Review: pull-request-runner-sweep

## Scope

Target: `skills/pull-request-runner-sweep/` (SKILL.md, references/{runs-and-cancel,non-interactive}.md, examples/01).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — `skills-ref` isn't provisioned in this repository; `scripts/validate_skills.py` (the repository's frontmatter, body-size, and asset validator behind `task test`, CLAUDE.md §"Command entry points") ran in its place.
Narrowing: the changes of `feat/serial-pr-flow` (`origin/develop...386a9a51`) plus the full validator run and a load-trigger and broken-reference scan over every asset; unchanged sections were judged only through the validator.
Explicitly out of scope: runtime behavior of the skill, Vale/markdown style (handled by `task lint`), dispatched agents beyond confirming the orchestration direction.

## Summary

- Critical: 1
- Warning: 0
- Suggestion: 0
- Info: 0

Go/no-go: FAIL — one Critical
Next concrete action: add a load trigger for the example

## Findings

### Critical

- [ ] [skill-management.load-trigger] `examples/01-three-prs-one-current.md` has no load-trigger phrase in SKILL.md (pre-existing on develop).
      Where: skills/pull-request-runner-sweep/SKILL.md:76 (no ## Examples section).
      Fix: add an ## Examples section with "Read examples/01-three-prs-one-current.md when …".
      Verify: grep the example path in SKILL.md.

### Warning

- none

### Suggestion

- none

### Info

- none

## Processing log
