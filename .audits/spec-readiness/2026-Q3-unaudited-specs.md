---
audit-type: spec-readiness
repo-revision: dac0375f8e7aa201496253940c64fa003e15dcd0
created: 2026-09-13
scope: 13 specs
status: closed
---

# Spec Readiness Audit — 2026-Q3, the 13 specs the first 2026-Q3 run didn't cover

## Scope

A supplement to `.audits/spec-readiness/2026-Q3.md` for the 13 specs that run didn't cover (spec-drift-audit 2026-Q4 finding F120, #587), audited by the `spec-readiness-reviewer` agent at `dac0375` against `spec/project/spec-readiness/en.md`, all three dimensions, with `python3 scripts/check_section_refs.py --report` as a triage aid whose matches were each read against the cited target:

`spec/frontend/source-code-review`, `spec/project/error-tracking`, `spec/project/rest-api-design`, `spec/project/test-falsifiability`, `spec/project/continuous-delivery`, `spec/project/continuous-integration`, `spec/project/e2e-failure-diagnosis`, `spec/project/github-actions-best-practices`, `spec/claude/dispatch-brief`, `spec/claude/claim-provenance`, `spec/claude/research-plan-implement`, `spec/project/artifact-signing`, `spec/project/defect-class-guards`.

## Summary

Per-spec counts, exact (finding F121 asked for a per-spec breakdown instead of tranche aggregates):

| Spec | Critical | Warning | Suggestion | Info |
|---|---|---|---|---|
| `frontend/source-code-review` | 0 | 0 | 0 | 1 |
| `project/error-tracking` | 0 | 0 | 0 | 0 |
| `project/rest-api-design` | 0 | 0 | 0 | 0 |
| `project/test-falsifiability` | 0 | 0 | 0 | 0 |
| `project/continuous-delivery` | 0 | 0 | 0 | 1 |
| `project/continuous-integration` | 0 | 0 | 0 | 1 |
| `project/e2e-failure-diagnosis` | 0 | 0 | 1 | 2 |
| `project/github-actions-best-practices` | 0 | 0 | 0 | 1 |
| `claude/dispatch-brief` | 0 | 0 | 0 | 1 |
| `claude/claim-provenance` | 0 | 0 | 0 | 1 |
| `claude/research-plan-implement` | 0 | 0 | 0 | 0 |
| `project/artifact-signing` | 1 | 0 | 0 | 1 |
| `project/defect-class-guards` | 0 | 0 | 1 | 1 |
| **Total** | **1** | **0** | **2** | **10** |

**Verdict:** 12 of 13 specs carry no promotion-blocking finding; `artifact-signing` carried one load-bearing Open Question, settled in the same change.

## Findings

### Critical

- [x] **`artifact-signing` — load-bearing Open Question.** Whether §C's platform provenance attestation applies to a private repository without GitHub Enterprise Cloud was open while §C's MUST carried no carve-out (`en.md:143` against `en.md:51`).
  - Fix: surveyed on 2026-09-13: the user-owned `nolte` account has no Enterprise Cloud and none of its three private repositories publishes OCI artifacts. The Open Question is recorded as settled, §C gains a Cosign-provenance MAY for a private publisher, and the verification criterion names the matching `cosign verify-attestation` check (EN and DE).

### Suggestion

- [x] **`e2e-failure-diagnosis` — criteria without checkbox form** (`en.md:145-153`, `de.md:145-153`). Fix: all seven criteria per language now use `- [ ]`.
- [x] **`defect-class-guards` — single-source sister-repository citations** without the reason that suffices (`en.md` References). Fix: one sentence states why first-hand reading of an issue with one canonical location is the triangulation `research-triangulate` can ask for (EN and DE).

### Info

- [x] **Missing `Readers:` line** in `e2e-failure-diagnosis`, `dispatch-brief`, and `defect-class-guards`. Fix: each gains one in EN and DE.
- [x] **Resolver noise** in `frontend/source-code-review`, `continuous-delivery`, `continuous-integration`, `e2e-failure-diagnosis`, `github-actions-best-practices`, `claim-provenance`, and `artifact-signing`: genitive `§D's` and arrow-list `§1 → §A` forms reported as resolving in no language, every one read and confirmed as resolving. Fix: the resolver treats `'` and `→` as a label boundary, which dropped the advisory count from 347 to 329; the remaining forms name issue topics rather than headings and stay advisory.

## Processing log

- 2026-09-13 — audit run by `spec-readiness-reviewer` at `dac0375`: 13 specs read in full, about 50 resolver matches triaged by reading each target heading, no file modified.
- 2026-09-13 — every finding above fixed in the same change (#587).
