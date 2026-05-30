# Spec Readiness

Status: draft

## Context

Rules for auditing a specification's readiness for downstream implementation. Readers:
the spec-readiness-reviewer agent and human reviewers.

## Requirements

- The audit MUST check three dimensions: contradictions (intra- and cross-spec),
  audience fit, and domain completeness (Requirement <-> Acceptance Criterion coverage,
  load-bearing Open Questions, and ghost references).
- Every finding MUST cite a concrete spec path and a line or section reference.
- Findings MUST be classified with the canonical severity scale defined in
  `spec/claude/review-plan/` (Critical / Warning / Suggestion / Info).
- A MUST vs MUST NOT pair on the same subject MUST be classified Critical.
- An Acceptance Criterion that ties back to no Requirement or Goal (an orphan) MUST be
  classified Warning.

## Acceptance Criteria

- [ ] The report is severity-sorted and uses only the canonical severity buckets.
- [ ] Each finding cites a spec path and a line or section reference.
- [ ] Same-subject MUST vs MUST NOT contradictions are reported as Critical.
- [ ] Orphan Acceptance Criteria are reported as Warning.
