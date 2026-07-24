---
review-type: spec-readiness
target: spec/portfolio/tech-stack/
target-kind: spec
specs-applied:
  - spec/project/spec-readiness/@66d6513791380914c73b78c360b5740c29ef13ba
  - spec/claude/review-plan/@e75ffbbafaf33cd55ae46dda966894add3ae01e4
repo-revision: 80efd0c449cf6ea0c4b3574a5e560a06304e1145
created: 2026-07-25
status: open
---

## Scope

Pre-promotion readiness audit of `spec/portfolio/tech-stack/` (canonical `en.md` plus the `de.md`
translation, both read in full) ahead of the `Status: draft` → `Status: accepted` promotion recorded
in issue #457, trigger 1. Run by the read-only `nolte-shared:spec-readiness-reviewer` agent inside
the linked worktree `tech-stack-rendering` (branch `feat/tech-stack-rendering`), persisted here per
`spec/project/parallel-working-copies/` §Audit artefacts in multiple worktrees and per
`spec/project/spec-readiness/` §Audit artifact (single-spec pre-promotion runs follow the
`review-plan` format). Trigger class: **pre-promotion**.

Reviewed across all three readiness dimensions: contradictions (intra-spec and cross-spec against
the sibling `spec/portfolio/tech-stack-discovery/`), audience fit, and domain completeness
(Requirements ↔ Acceptance-Criteria coverage, load-bearing Open Questions, ghost references).
Ghost references were resolved against the working tree, not assumed.

Explicitly out of scope: prose linting (Vale), the sibling spec's own findings (tracked in
`.audits/spec-readiness/portfolio-tech-stack-discovery.md`), and downstream implementation
conformance (that's `spec-drift-audit`). Not-yet-implemented downstream work was classified as
pending, not as a spec-text defect — see §Findings → Info.

Prior audit: `.audits/spec-readiness/2026-Q3.md` (2026-07-24, tranche T6). Both prior findings
against this spec pair are resolved-since-last-audit; zero recurring.

## Summary

- **Critical:** 0
- **Warning:** 4
- **Suggestion:** 0
- **Info:** 3

**Go/no-go:** **GO** for promotion out of `Status: draft`. Zero Critical findings and zero
unresolved load-bearing Open Questions, which is the promotion gate defined in
`spec/project/spec-readiness/` §Audit scope and cadence. The Warning-class items are
Requirement-to-Acceptance-Criteria coverage gaps that a careful reader navigates around; they don't
block promotion and stay open here as the tracked backlog.

## Findings

### Warning

- [ ] [tech-stack.inheritance-semantics] The MUST NOT against silent divergence (a repository that
      ships a `kind: docs` artefact without inheriting the global `docs` entry and without an
      explicit override is a `Warning` audit finding) is stated only inside the §Portfolio audit
      integration severity table and has no dedicated Acceptance Criterion, unlike the sibling
      override, regroup, and deprecation-chain rules.
      Where: `spec/portfolio/tech-stack/en.md` §Inheritance semantics (and the matching DE section).
      Fix: add one Acceptance Criterion asserting that the silent-divergence check produces zero
      `Warning` findings on the current HEAD.
      Verify: the §Acceptance Criteria list carries a silent-divergence bullet; a re-run of this
      readiness audit reports the gap closed.

- [ ] [tech-stack.inheritance-semantics] The MUST that a `status: deprecated` global entry stays
      inherited until each consumer overrides it, with the audit emitting a `Suggestion` after one
      closed sprint, carries no dedicated Acceptance Criterion.
      Where: `spec/portfolio/tech-stack/en.md` §Inheritance semantics (and the matching DE section).
      Fix: add one Acceptance Criterion asserting that the deprecated-still-inherited check produces
      zero unresolved `Suggestion` findings beyond the one-closed-sprint window.
      Verify: the §Acceptance Criteria list carries a deprecated-still-inherited bullet.

- [ ] [tech-stack.kind-enum] The SHOULD that an `other`-classified entry escalates to an enum
      revision after two consecutive quarterly audits or 180 days has no corresponding Acceptance
      Criterion, so the escalation window isn't mechanically checkable.
      Where: `spec/portfolio/tech-stack/en.md` §Kind enum (and the matching DE section).
      Fix: add one Acceptance Criterion asserting that no `kind: other` entry has exceeded the
      escalation window without an enum-revision proposal.
      Verify: the §Acceptance Criteria list carries an `other`-escalation bullet.

- [ ] [tech-stack.documentation-rendering] The two SHOULD items in §Documentation rendering — the
      Mermaid kind-distribution diagram and the per-consumer delta view — carry no Acceptance
      Criterion; the single rendering AC covers only the MUST-level badges and group-first ordering.
      Where: `spec/portfolio/tech-stack/en.md` §Documentation rendering (and the matching DE section).
      Fix: extend the rendering Acceptance Criterion, or add one alongside it, to name the delta view
      and the kind-distribution diagram.
      Verify: the §Acceptance Criteria list names both SHOULD-level rendering artefacts.

### Info

- [ ] [spec-readiness.open-questions] Open-Questions closure phrasing is asymmetric across the
      sibling pair: this spec documents its resolutions without a date, while
      `tech-stack-discovery` cites `2026-06-06` plus a decision log. Both sections are genuinely
      closed; the asymmetry is cosmetic only. No action required.
      Where: `spec/portfolio/tech-stack/en.md` §Open Questions.
      Fix: n/a — cosmetic.
      Verify: n/a — cosmetic.

- [ ] [tech-stack.portfolio-audit-integration] The `acknowledged-missing-signal` marker is used
      consistently across this spec's rationale-downgrade clause, the sibling spec, and the capture
      skill's signal-source map, but its exact string format is never formally specified — only
      implied. Low-value tightening opportunity, not a defect.
      Where: `spec/portfolio/tech-stack/en.md` §Portfolio audit integration (rationale-downgrade
      clause).
      Fix: n/a — optional tightening, deliberately left free-form.
      Verify: n/a.

- [ ] [tech-stack.documentation-rendering] The rendering Acceptance Criterion and the
      portfolio-audit tech-stack-coverage Acceptance Criterion were unsatisfied at review time
      because the downstream work hadn't landed, not because the spec text is defective. The
      rendering half lands in this same pull request (issue #457, trigger 3); the audit-coverage
      half stays pending against `spec/portfolio/portfolio-management/`. Correctly classified as
      pending downstream work, so it isn't a promotion blocker.
      Where: `spec/portfolio/tech-stack/en.md` §Acceptance Criteria (rendering and audit-coverage
      bullets).
      Fix: n/a for the spec — the rendering is implemented in this pull request; the audit-coverage
      bullet follows when the `portfolio-audit` extension lands.
      Verify: `docs/en/portfolio/index.md` and `docs/de/portfolio/index.md` carry a global
      tech-stack section plus per-repository tech-stack subsections.

## Processing log

2026-07-25—promotion-gate—readiness audit run pre-promotion, verdict GO (0 Critical, 0 load-bearing Open Questions); `Status: draft` → `Status: accepted` applied to en.md and de.md—agent:spec-readiness-reviewer + human-directed main session
2026-07-25—documentation-rendering-SHOULD—the delta-view SHOULD this plan's fourth Warning refers to is implemented in the same pull request (`scripts/docs/gen_portfolio.py`); the Acceptance-Criteria gap itself stays open—agent:claude
