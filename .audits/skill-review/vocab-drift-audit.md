---
review-type: skill-review
target: "skills/vocab-drift-audit/SKILL.md"
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

# Skill Review: vocab-drift-audit

## Scope

Target: `skills/vocab-drift-audit/SKILL.md` (~77 lines after fix). No subdirs.

Validator: override — external skill-structure validator not yet provisioned (tracked by Open Question in `spec/claude/skill-review/`).

Best-practices pass: under the 500-line cap, clear defaults (severity floor `low`, `pip-audit` / `npm audit` per ecosystem), procedures over declarations, fixed report-section order documented as a hard rule (effectively a Gotchas equivalent for downstream parsers).

## Summary

- BLOCKER: 1
- WARNING: 0
- SUGGESTION: 1
- INFO: 0

Go/no-go: PASS — all closed in this PR.

## Findings

### BLOCKER

- [x] [skill-vs-agent.rationale-documentation] No rationale section.
      Fix: Added "## Why this is a skill, not an agent" with conversation-flow output, interactivity for destructive defaults, orchestrator role, plus a counter-dimension.
      Verify: `grep -nE '^## (Why|Rationale)' skills/vocab-drift-audit/SKILL.md` matches.

### SUGGESTION

- [x] [skill-management.tag-vocabulary] No `tags:`; starter vocab `audit` applies.
      Fix: Added `tags: [audit]`.
      Verify: `grep '^tags:' skills/vocab-drift-audit/SKILL.md` shows `tags: [audit]`.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-04-30 — rationale-documentation — added rationale section — verified: grep
2026-04-30 — tag-vocabulary — added `tags: [audit]` — verified: grep
