---
review-type: spec-readiness
target: spec/portfolio/tech-stack-discovery/
target-kind: spec
specs-applied:
  - spec/project/spec-readiness/@66d6513791380914c73b78c360b5740c29ef13ba
  - spec/claude/review-plan/@e75ffbbafaf33cd55ae46dda966894add3ae01e4
repo-revision: 80efd0c449cf6ea0c4b3574a5e560a06304e1145
created: 2026-07-25
status: open
---

## Scope

Pre-promotion readiness audit of `spec/portfolio/tech-stack-discovery/` (canonical `en.md` plus the
`de.md` translation, both read in full) ahead of the `Status: draft` → `Status: accepted` promotion
recorded in issue #457, trigger 1. Run by the read-only `nolte-shared:spec-readiness-reviewer` agent
inside the linked worktree `tech-stack-rendering` (branch `feat/tech-stack-rendering`), persisted
here per `spec/project/parallel-working-copies/` §Audit artefacts in multiple worktrees and per
`spec/project/spec-readiness/` §Audit artifact. Trigger class: **pre-promotion**.

Reviewed across all three readiness dimensions: contradictions (intra-spec and cross-spec against
the sibling schema spec `spec/portfolio/tech-stack/`, with particular attention to the delimitation
MUST NOT that forbids restating the entry schema, the `kind` enum, the inheritance contract, or the
audit-severity table), audience fit against the repository's `AUDIENCES.md`, and domain completeness
(Requirements ↔ Acceptance-Criteria coverage, load-bearing Open Questions, ghost references).

Explicitly out of scope: prose linting (Vale), the sibling schema spec's own findings (tracked in
`.audits/spec-readiness/portfolio-tech-stack.md`), and downstream implementation conformance.

Prior audit: `.audits/spec-readiness/2026-Q3.md` (2026-07-24, tranche T6). The criticality mismatch
it raised against §Audiences (`secondary` versus `peripheral`) is resolved-since-last-audit
(commit `66d6513`, pull request #478); zero recurring.

## Summary

- **Critical:** 0
- **Warning:** 2
- **Suggestion:** 0
- **Info:** 2

**Go/no-go:** **GO** for promotion out of `Status: draft`. Zero Critical findings and zero
unresolved load-bearing Open Questions (the §Open Questions closure dated 2026-06-06 was verified
against git history rather than taken at face value). The delimitation contract with the sibling
schema spec holds: no schema field, enum value, inheritance rule, or severity level is restated
here. Every §Audiences bullet resolves against `AUDIENCES.md` or carries the in-text
tech-stack-specific-refinement disclaimer the spec's own Acceptance Criteria require, and the
JS/TS allowlist matches the capture skill's signal-source map row for row.

## Findings

### Warning

- [ ] [tech-stack-discovery.discovery-sequence] §Discovery sequence per repository carries eleven
      distinct MUST/SHOULD items, but only the JS/TS curated-allowlist slice has a narrowly testable
      Acceptance Criterion. The remainder rests on one coarse-grained criterion ("the capture skill
      implements the discovery sequence in the order documented; a skill-review confirms the order"),
      leaving individual behavioural MUSTs — notably "MUST NOT write a `tech_stack:` block until the
      maintainer has confirmed at least one round" — without an independently checkable criterion.
      Where: `spec/portfolio/tech-stack-discovery/en.md` §Requirements → Discovery sequence per
      repository (and the matching DE section).
      Fix: add one Acceptance Criterion for the confirmation-before-write MUST and one for the
      compare-against-the-active-global-stack-before-writing MUST, keeping the existing coarse
      criterion for the ordering itself.
      Verify: the §Acceptance Criteria list carries a confirmation-gate bullet; a re-run of this
      readiness audit reports the gap narrowed.

- [ ] [tech-stack-discovery.global-stack-curation] The MUST that every revision of
      `portfolio/tech-stack.yml` is routed through the standard pull-request workflow has no
      dedicated Acceptance Criterion. The rule is verifiable from `git log`, but the spec doesn't
      name that check, so nothing tells a reviewer how to confirm it.
      Where: `spec/portfolio/tech-stack-discovery/en.md` §Requirements → Global stack curation in
      `claude-shared` (and the matching DE section).
      Fix: add one Acceptance Criterion asserting that `git log --merges portfolio/tech-stack.yml`
      shows every revision arriving via a merged pull request.
      Verify: the §Acceptance Criteria list carries a pull-request-routing bullet.

### Info

- [ ] [tech-stack-discovery.audience-fit] The "Contributor reading the rendered docs during
      onboarding" bullet maps to the `AUDIENCES.md` entry "External contributors via pull request".
      The criticality alignment is correct (`peripheral` on both sides) and the mapping satisfies the
      relevant Acceptance Criterion by its letter, but the described surface (reading a rendered docs
      page) doesn't obviously match that entry's pull-request-authorship surface. Worth a maintainer
      glance at the next `AUDIENCES.md` revisit; no action required now.
      Where: `spec/portfolio/tech-stack-discovery/en.md` §Audiences → Direct consumers.
      Fix: n/a — reconcile opportunistically at the next `AUDIENCES.md` revisit.
      Verify: n/a.

- [ ] [tech-stack-discovery.acceptance-criteria] Two Acceptance Criteria were unsatisfied at review
      time because the downstream work hadn't landed: the capture skill's discovery-sequence
      conformance (pending a `skill-review` run; the skill directory exists and is actively built
      out) and the rendered-docs Benefits paraphrase with a backlink. The latter lands in this same
      pull request (issue #457, trigger 3). Both are pending downstream work, not spec-text defects,
      so neither blocks promotion.
      Where: `spec/portfolio/tech-stack-discovery/en.md` §Acceptance Criteria.
      Fix: n/a for the spec — the rendering half is implemented in this pull request; the
      skill-review half follows separately.
      Verify: `docs/en/portfolio/index.md` and `docs/de/portfolio/index.md` carry a Benefits
      paraphrase with a backlink to this spec.

## Processing log

2026-07-25—promotion-gate—readiness audit run pre-promotion, verdict GO (0 Critical, 0 load-bearing Open Questions, 0 ghost references); `Status: draft` → `Status: accepted` applied to en.md and de.md—agent:spec-readiness-reviewer + human-directed main session
2026-07-25—benefits-rendering-AC—the Benefits-paraphrase-with-backlink Acceptance Criterion is satisfied in the same pull request by `scripts/docs/gen_portfolio.py`; the remaining Warning-class Acceptance-Criteria gaps stay open—agent:claude
