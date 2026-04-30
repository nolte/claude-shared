---
review-type: skill-review
target: "skills/skill-agent-catalog-apply/SKILL.md"
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

# Skill Review: skill-agent-catalog-apply

## Scope

Target: `skills/skill-agent-catalog-apply/SKILL.md` (~205 lines after fix). No subdirs.

Validator: override — external skill-structure validator not yet provisioned (tracked by Open Question).

Best-practices pass: under the 500-line hard cap, clear defaults (plugin-mode = local plugin first, consumer-mode = external sources, alphabetical fallback), procedures over declarations, pre-existing "## Rationale" section already in place.

## Summary

- BLOCKER: 0
- WARNING: 0
- SUGGESTION: 1
- INFO: 1

Go/no-go: PASS — SUGGESTION closed; INFO acknowledged as accepted-as-is.

## Findings

### SUGGESTION

- [x] [skill-management.tag-vocabulary] No `tags:`; starter vocab `scaffolding` applies (cluster with `project-structure-apply`, `skill-management`, `spec`).
      Fix: Added `tags: [scaffolding]`.
      Verify: `grep '^tags:' skills/skill-agent-catalog-apply/SKILL.md` matches.

### INFO

- [x] [skill-management.body-length-soft-target] SKILL.md is 205 lines, above the ~150-line soft target but well under the 500-line / 5,000-token hard cap.
      Where: `skills/skill-agent-catalog-apply/SKILL.md` overall length.
      Fix: n/a (observation) — accepted as-is. The body covers operating-mode detection, the plugins block, source-roots data file, generator hook, dependencies, git hygiene, verification, and adding-roots-later: each subsection is load-bearing for the spec-application flow, and progressive disclosure to a `references/` file would split the operation map. Refactoring deferred until a concrete trigger surfaces.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-04-30 — tag-vocabulary — added `tags: [scaffolding]` — verified: grep
2026-04-30 — body-length-soft-target — observation acknowledged; no refactor this round — verified: n/a (observation)
