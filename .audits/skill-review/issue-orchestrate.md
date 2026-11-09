---
review-type: skill-review
target: "skills/issue-orchestrate/SKILL.md"
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

# Skill Review: issue-orchestrate

## Scope

Target: `skills/issue-orchestrate/` (SKILL.md, references/{closeout,dispatch-matching,measurement-discipline}.md, examples/01).
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
Next concrete action: move detail from the body into references/

## Findings

### Critical

- none

### Warning

- [ ] [skill-management.body-token-approaching] Validator: body ~4,996 tokens, inside the 4,500–5,000 warning band; any lane-mode addition would break the hard cap.
      Where: skills/issue-orchestrate/SKILL.md (whole body).
      Fix: move operation 5 steps 3–4 detail into references/dispatch-matching.md and fold duplicated prose into references.
      Verify: python3 scripts/validate_skills.py reports no body-token finding for this skill.

### Suggestion

- none

### Info

- [ ] [skill-review.frontmatter] The lane flag (`lane: true`) is defined in references/closeout.md, not in an Arguments section; the body only says "as a lane". Acceptable because the closeout reference is loaded at the step that branches on it.
      Where: skills/issue-orchestrate/references/closeout.md:33.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log
