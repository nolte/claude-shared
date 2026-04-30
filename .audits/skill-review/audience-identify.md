---
review-type: skill-review
target: "skills/audience-identify/SKILL.md"
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

# Skill Review: audience-identify

## Scope

Target: `skills/audience-identify/SKILL.md` (~74 lines after fix), `templates/audiences.template.md` referenced with load-trigger ("Write the artifact at the chosen location, using the template at templates/audiences.template.md").

Validator: override — external skill-structure validator not yet provisioned (tracked by Open Question in `spec/claude/skill-review/`).

Best-practices pass: under the 500-line cap, clear default for relationship-category enumeration order, procedures over declarations, no Gotchas needed (the spec itself enumerates the non-obvious rules).

## Summary

- BLOCKER: 1
- WARNING: 0
- SUGGESTION: 1
- INFO: 0

Go/no-go: PASS — all closed in this PR.

## Findings

### BLOCKER

- [x] [skill-vs-agent.rationale-documentation] No rationale section.
      Where: `skills/audience-identify/SKILL.md` pre-fix.
      Fix: Added "## Why this is a skill, not an agent" naming mid-flow interactivity (per-category dialogue), persistent on-disk artifact, confirmed-vs-assumed gating, plus a counter-dimension.
      Verify: `grep -nE '^## (Why|Rationale)' skills/audience-identify/SKILL.md` matches.

### SUGGESTION

- [x] [skill-management.tag-vocabulary] No `tags:` field; starter vocab `audience` applies.
      Fix: Added `tags: [audience]`.
      Verify: `grep '^tags:' skills/audience-identify/SKILL.md` shows `tags: [audience]`.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-04-30 — rationale-documentation — added rationale section — verified: grep
2026-04-30 — tag-vocabulary — added `tags: [audience]` — verified: grep
