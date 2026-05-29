# Example: defer to backlog

Feature `F-9` (`wire-renovate-automerge-exclusion`) reached `done` mid-sprint. The sprint's value-verifying feature hasn't shipped yet, so the operator wants a single sprint-summary post later rather than a per-feature post now.

## 1–3. Resolve, derive, suggest

The skill resolves the event and derives the briefing as in example 01. Because `F-9` is a non-value-verifying mid-sprint feature and the sprint's `verifies_sprint_value` feature is still `in_progress`, the skill suggests **Choice 3 (defer to backlog)**. The operator confirms Choice 3 with the reason "fold into the sprint-summary post once the value-verifying feature ships".

## 4–5. Write the deferral artefact

The skill writes `project/blog-triggers/wire-renovate-automerge-exclusion.yml` in the source consumer:

```yaml
id: F-9
slug: wire-renovate-automerge-exclusion
title: Wire Renovate automerge exclusion
description: Hold gh-plumbing bumps out of automerge even when checks are green.
acceptance_criteria:
  - "A gh-plumbing Renovate PR is not auto-merged while the exclusion applies."
roadmap_item: R-3
repo: nolte/claude-shared
done_commit: a2936de
deferred_at: 2026-05-29T10:14:00Z
deferral_reason: "fold into the sprint-summary post once the value-verifying feature ships"
status: deferred
```

No `blog-author` dispatch happens. `sprint-review` surfaces this unconsumed deferral at sprint close. When a later trigger-run on `F-9` (or the operator) picks Choice 1 or 2, the skill flips `status: deferred → consumed` on this same file rather than writing a second artefact.
