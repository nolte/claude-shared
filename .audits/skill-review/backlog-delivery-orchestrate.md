---
review-type: skill-review
target: "skills/backlog-delivery-orchestrate/SKILL.md"
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

# Skill Review: backlog-delivery-orchestrate

## Scope

Target: `skills/backlog-delivery-orchestrate/` (SKILL.md + references/{lanes,merge-train,state-and-authorisation,fresh-session}.md, scripts/merge-train.sh, examples/01).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — `skills-ref` isn't provisioned in this repository; `scripts/validate_skills.py` (the repository's frontmatter, body-size, and asset validator behind `task test`, CLAUDE.md §"Command entry points") ran in its place.
Narrowing: the changes of `feat/serial-pr-flow` (`origin/develop...386a9a51`) plus the full validator run and a load-trigger and broken-reference scan over every asset; unchanged sections were judged only through the validator.
Explicitly out of scope: runtime behavior of the skill, Vale/markdown style (handled by `task lint`), dispatched agents beyond confirming the orchestration direction.

## Summary

- Critical: 0
- Warning: 2
- Suggestion: 0
- Info: 1

Go/no-go: CONDITIONAL — both Warnings fixed
Next concrete action: align the hard rule and operation 5 with references/merge-train.md

## Findings

### Critical

- none

### Warning

- [ ] [skill-management.progressive-disclosure] The red-check hard rule says "stop that PR", contradicting the fix-forward and classified-rerun path in references/merge-train.md and spec rule 5.
      Where: skills/backlog-delivery-orchestrate/SKILL.md:100.
      Fix: reword the rule to: classify, repair by fix-forward or one classified rerun, set the lane aside on a second red.
      Verify: grep the hard rule; it names fix-forward and matches merge-train.md §"Acting on the script's exit".
- [ ] [skill-management.progressive-disclosure] Operation 5 still says "continue with the next PR; when the train is empty", the pre-serial wording that ignores train turns and committed-locally lanes.
      Where: skills/backlog-delivery-orchestrate/SKILL.md:76.
      Fix: reword to "start the next train turn; when no lane is committed-locally and planned lanes remain, return to operation 3".
      Verify: read operation 5 against references/merge-train.md §"Each turn" and references/lanes.md §"Round planner".

### Suggestion

- none

### Info

- [ ] [skill-review.duplicate-prevention] The cancel predicate exists twice: scripts/merge-train.sh (branch attribution) and pull-request-runner-sweep references/runs-and-cancel.md (head-SHA attribution, used by its new --non-interactive mode); both carry the same guards (event, develop/main, delivery path), which the brief requires.
      Where: scripts/merge-train.sh cancel_waiting(); skills/pull-request-runner-sweep/references/runs-and-cancel.md.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log
