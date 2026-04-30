---
review-type: skill-review
target: "skills/pull-request-merge/SKILL.md"
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

# Skill Review: pull-request-merge

## Scope

Target: `skills/pull-request-merge/SKILL.md` (~205 lines after fix). No subdirs.

Validator: override — external skill-structure validator not yet provisioned (tracked by Open Question).

Best-practices pass: under the 500-line hard cap, clear defaults (squash-only, `--draft` not allowed at merge, wait-mode opt-in with bounded caps), procedures over declarations, "Wait mode" subsection plus dedicated step-7b audit are the closest thing to a Gotchas section (they explain non-obvious automation behavior the agent will trip over otherwise — automerge SUCCESS != real merge).

## Summary

- BLOCKER: 1
- WARNING: 0
- SUGGESTION: 1
- INFO: 1

Go/no-go: PASS — BLOCKER and SUGGESTION closed; INFO acknowledged as accepted-as-is.

## Findings

### BLOCKER

- [x] [skill-vs-agent.rationale-documentation] No rationale section.
      Fix: Added "## Why this is a skill, not an agent" (externally-visible mutations, orchestrator that chains review and security-review, wait-mode visible-status-per-round requirement, plus counter-dimension).
      Verify: `grep -nE '^## (Why|Rationale)' skills/pull-request-merge/SKILL.md` matches.

### SUGGESTION

- [x] [skill-management.tag-vocabulary] No `tags:`; starter vocab `pull-request` applies (cluster with `pull-request-create`).
      Fix: Added `tags: [pull-request]`.
      Verify: `grep '^tags:' skills/pull-request-merge/SKILL.md` matches.

### INFO

- [x] [skill-management.body-length-soft-target] SKILL.md is 205 lines, above the ~150-line soft target from `skill-management` §Recommendations but well under the 500-line / 5,000-token hard cap.
      Where: `skills/pull-request-merge/SKILL.md` overall length.
      Fix: n/a (observation) — accepted as-is. The body covers automerge gating, wait mode, and the step-7b audit: each subsection is load-bearing for the contract, and progressive disclosure to a `references/` file would split semantically tightly coupled rules. Refactoring deferred until a concrete trigger surfaces.
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-04-30 — rationale-documentation — added rationale section — verified: grep
2026-04-30 — tag-vocabulary — added `tags: [pull-request]` — verified: grep
2026-04-30 — body-length-soft-target — observation acknowledged; no refactor this round — verified: n/a (observation)
