---
review-type: spec-readiness
trigger: pre-promotion
target: wave-1 draft promotion candidates (6 specs)
specs-applied:
  - spec/project/spec-readiness/en.md
  - spec/claude/review-plan/en.md
repo-revision: develop @ 7020d98
created: 2026-06-06
status: open
---

# Spec Readiness Audit — Wave-1 Pre-Promotion (2026-06-06)

Pre-promotion readiness audit of six `Status: draft` specs the operator intends to
promote to `Status: accepted` (the portfolio's first spec promotions). One
`spec-readiness-reviewer` agent per spec. Promotion gate per
`spec/project/spec-readiness/` §Triggers line 71: a spec with unresolved Critical
findings MUST NOT be promoted.

## Verdicts and severity counts

| Spec | Critical | Warning | Suggestion | Info | Verdict |
|---|---:|---:|---:|---:|---|
| project/lektorat | 0 | 4 | 1 | 3 | **GO** |
| project/post-writing-style | 0 | 3 | 0 | 4 | **GO** |
| project/release-notes-audience-analysis | 2 | 3 | 0 | 3 | NO-GO |
| project/audience-identification | 1 | 2 | 0 | 2 | NO-GO |
| project/blog-author | 2 | 2 | 0 | 3 | NO-GO |
| project/spec-driven-development | 1 | 2 | 0 | 2 | NO-GO |

Promoted in this wave: **lektorat**, **post-writing-style** (both GO, zero Critical).

## GO — promoted

### project/lektorat — GO
Open Questions: Q1 (API-reference scope) parking-lot; Q2 (batched-vs-per-file dispatch) parking-lot. 0 load-bearing.
Warnings (tracked, non-blocking): severity-scale-divergence vs `review-plan` canonical scale; 3 Requirement-without-testable-AC gaps (Vale-dedup MUST, D5 register-mismatch severity, language-handling line-mapping). Suggestion: corridor-override ±50% ambiguity. Info: no cross-ref to `lektorat-auto-revise`; audience-artefact-missing AC needs setup precondition.

### project/post-writing-style — GO
Open Questions: Q1 (10 EN posts readability gate), Q2 (5 DE posts), Q3 (third override case) — all parking-lot, all data-gated on a blog corpus of ~2-3 posts. 0 load-bearing.
Warnings (tracked, non-blocking): W-1 14 MUSTs without a testable AC (most are reviewer-judgement by design per en.md:172); W-2 untracked forward-reference at line 185 (correction channel); W-3 Goal 6 "stay personal-blog-scoped" is a scope exclusion mislabelled as a Goal (move to Non-Goals). Info: a-4 MUST/Provisional tension; DE-exemption lifecycle cross-ref.

## NO-GO — promotion blocked, Critical findings to resolve

### project/release-notes-audience-analysis — NO-GO (2 Critical)
- **C-1** Ghost assertion (en.md:49): claims `pull-request-workflow` "already routes security-sensitive diffs through" a `security-review` skill. No `security-review` skill exists; `pull-request-workflow` has no security routing. Fix: remove/correct the claim, or build the skill + wire pull-request-workflow.
- **C-2** AC line 68 fails today: requires `release-automation` §Non-Goals to cross-link this spec; it does not. Fix: add one cross-reference line to `spec/project/release-automation/{en,de}.md` §Non-Goals.
- Warnings: W-1 AC-69 relies on undeclared `spec-drift-audit` capability; W-2 `audience-identification` has no `§Artifact location` heading; W-3 MUST line 32 ordering constraint has no AC. 0 Open Questions.

### project/audience-identification — NO-GO (1 Critical)
- **C-1** Ghost section: `§Artifact location` cited 3× (en.md:24,44,65 + DE) but no such heading exists; rule lives in the SHOULD bullet at line 46. Fix: add `### Artifact location` heading before line 46 (EN+DE), or rewrite the 3 anchors.
- Warnings: AC-55 (readme-structure cross-ref absent); AC-60 (spec-drift-audit audience-drift capability absent). Open Question Q5 (security/privacy/SLA consumer) parking-lot.

### project/blog-author — NO-GO (2 Critical)
- **C-1** Cross-spec MUST conflict: blog-author §Handover routes (en.md:186-188) tells authors to run `lektorat-apply` on blog post pairs, but `lektorat` §Scope/§Non-Goals (en.md:34,41,45) excludes blog posts and forbids scope widening. Resolution (audit Option C): clarify lektorat §Non-Goals to scope the exclusion to `src/content/` trees and admit blog posts as an opt-in consumer surface; mirror in blog-author route. Symmetric — must fix both before either is "accepted".
- **C-2** Load-bearing OQ1 (en.md:240): per-consumer adoption of target-state handover route; condition 1 (lektorat leaves draft) lands in this wave. Fix: resolve OQ1 text + the `nolte/blog/CLAUDE.md` editor-entry update.
- Warnings: W-1 consumer-contract MUST (line 51) has no AC; W-2 DE link anchor/href mismatch (de.md:236). OQ2/OQ3 parking-lot.

### project/spec-driven-development — NO-GO (1 Critical)
- **C-1** Load-bearing OQ1 (en.md:61-63): revisit threshold ("≥3 implementation PRs missing `Refs spec/`") is demonstrably met — `.audits/spec-drift/2026-Q2.md` documents 7 such PRs. Fix: resolve the OQ — either commit to extending gh-plumbing `reusable-pr-lint` with a `Refs spec/` assertion (+ feature item), or record a deliberate waiver with a new concrete trigger.
- Warnings: AC5 orphan (cross-refs not in §Open Questions body); MUST(this) vs SHOULD(pull-request-workflow) escalation mismatch. OQ1 load-bearing (the Critical).

## Processing log

- 2026-06-06 — lektorat — promoted draft→accepted, 0 Critical — verified by this audit
- 2026-06-06 — post-writing-style — promoted draft→accepted, 0 Critical — verified by this audit
- 2026-06-06 — audience-identification — Critical C-1 (ghost `§Artifact location`) resolved: three `§`-anchor references rewritten to point to the artifact-storage SHOULD in Requirements (EN+DE); promoted draft→accepted
- 2026-06-06 — release-notes-audience-analysis — Critical C-1 reclassified as false-Critical (the `security-review` skill is a Claude Code built-in and `pull-request-merge` SKILL.md:65 routes security-sensitive diffs through it); reference at en.md:49 corrected to name `pull-request-merge` (EN+DE). Critical C-2 resolved: cross-link added to `release-automation` §Non-Goals (EN+DE), satisfying AC line 68. Promoted draft→accepted
- 2026-06-06 — spec-driven-development — Critical C-1 (load-bearing OQ1, threshold met) resolved by recorded waiver: CI enforcement deliberately deferred, manual operator enforcement continues, new post-promotion revisit trigger set; Warning AC5 closed by adding recursion cross-references into §Open Questions (EN+DE). Promoted draft→accepted
