---
review-type: skill-review
target: "skills/project-structure-apply/SKILL.md"
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

# Skill Review: project-structure-apply

## Scope

Target: `skills/project-structure-apply/SKILL.md` (~109 lines after fix). No subdirs.

Validator: override — external skill-structure validator not yet provisioned (tracked by Open Question).

Best-practices pass: under the 500-line cap (109 lines), clear defaults (`_extends:` pointers, fallback paths for missing release tag), procedures over declarations, hard rules cover the destructive-action invariants (Gotchas equivalent for the GitHub-API edge cases like `repository_selection: selected`).

## Summary

- BLOCKER: 1
- WARNING: 0
- SUGGESTION: 1
- INFO: 0

Go/no-go: PASS — all closed in this PR.

## Findings

### BLOCKER

- [x] [skill-vs-agent.rationale-documentation] No rationale section.
      Fix: Added "## Why this is a skill, not an agent" (per-item user approval, conversation-flow output, network-side actions need user gating, plus counter-dimension).
      Verify: `grep -nE '^## (Why|Rationale)' skills/project-structure-apply/SKILL.md` matches.

### SUGGESTION

- [x] [skill-management.tag-vocabulary] No `tags:`; starter vocab `scaffolding` applies.
      Fix: Added `tags: [scaffolding]`.
      Verify: `grep '^tags:' skills/project-structure-apply/SKILL.md` matches.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-04-30 — rationale-documentation — added rationale section — verified: grep
2026-04-30 — tag-vocabulary — added `tags: [scaffolding]` — verified: grep
