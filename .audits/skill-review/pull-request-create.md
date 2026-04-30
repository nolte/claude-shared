---
review-type: skill-review
target: "skills/pull-request-create/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "d0e50278c7f1b531620c474b1fac3df6952e0597+uncommitted-best-practices-extension"
  - slug: skill-vs-agent
    revision: "d0e50278c7f1b531620c474b1fac3df6952e0597"
  - slug: review-plan
    revision: "d0e50278c7f1b531620c474b1fac3df6952e0597"
  - slug: skill-review
    revision: "d0e50278c7f1b531620c474b1fac3df6952e0597+uncommitted-external-validator-and-best-practices-extensions"
repo-revision: "d0e50278c7f1b531620c474b1fac3df6952e0597"
created: "2026-04-30"
status: complete
---

# Skill Review: pull-request-create

## Scope

Target: `skills/pull-request-create/SKILL.md` (~150 lines after fix). No subdirs.

Validator: override — external skill-structure validator not yet provisioned (tracked by Open Question).

Best-practices pass: under the 500-line cap, just at the 150-line soft target, clear defaults (rebase vs merge recommendation, `--draft` default), procedures over declarations, embedded body template for the 5-section PR body acts as the load-trigger-equivalent for reviewers.

## Summary

- BLOCKER: 1
- WARNING: 0
- SUGGESTION: 1
- INFO: 0

Go/no-go: PASS — all closed in this PR.

## Findings

### BLOCKER

- [x] [skill-vs-agent.rationale-documentation] No rationale section.
      Fix: Added "## Why this is a skill, not an agent" (externally-visible action gating, mid-flow interactivity, conversation-flow output, plus counter-dimension).
      Verify: `grep -nE '^## (Why|Rationale)' skills/pull-request-create/SKILL.md` matches.

### SUGGESTION

- [x] [skill-management.tag-vocabulary] No `tags:`; starter vocab `pull-request` applies.
      Fix: Added `tags: [pull-request]`.
      Verify: `grep '^tags:' skills/pull-request-create/SKILL.md` matches.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-04-30 — rationale-documentation — added rationale section — verified: grep
2026-04-30 — tag-vocabulary — added `tags: [pull-request]` — verified: grep
