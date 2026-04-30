---
review-type: skill-review
target: "skills/agent-review/SKILL.md"
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

# Skill Review: agent-review

## Scope

Target: `skills/agent-review/SKILL.md` (~98 lines after fix), `templates/plan.template.md` referenced with load-trigger ("Draft the plan from templates/plan.template.md").

Validator: override — external skill-structure validator not yet provisioned (tracked by Open Question).

Best-practices pass: under the 500-line cap, clear defaults (canonical EN spec source, single-shot per agent), procedures over declarations, hard rules cover the bidirectional tool-scope check (effectively a Gotchas equivalent for the agent-vs-skill audit non-obvious cases). Pre-existing "## Why this is a skill, not an agent" rationale section already in place.

## Summary

- BLOCKER: 0
- WARNING: 0
- SUGGESTION: 1
- INFO: 0

Go/no-go: PASS — only the SUGGESTION applied.

## Findings

### SUGGESTION

- [x] [skill-management.tag-vocabulary] No `tags:`; starter vocab `review` applies (cluster with `skill-review`, `audience-review`).
      Fix: Added `tags: [review]`.
      Verify: `grep '^tags:' skills/agent-review/SKILL.md` matches.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-04-30 — tag-vocabulary — added `tags: [review]` — verified: grep
