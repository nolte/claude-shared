# Requirements — Release regression scope (targeted E2E from the change set)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Dispatched by `issue-orchestrate` as the requirements gate for issue #376
before decomposition. `c_d` is an uncertainty proxy (self-consistency-derived),
not a calibrated probability. A requirement is `confirmed` only after an explicit
teach-back / authoritative operator choice.
-->

## Bounded context

- **What:** A capability that, from the **change-set of a release**, derives the impacted topic areas (Themengebiete) and determines the **minimal-but-complete-within-area** regression / E2E test scope that must pass before shipping.
- **For whom:** The release operator / maintainer of a code-bearing repository, invoking it before rollout.
- **Guarantee triad:** *zielgenau* (only impacted areas gate the release), *zeitnah* (the selected subset runs fast enough not to block rollout), *vollständig-im-Bereich* (complete regression coverage of the functional requirements within each impacted area — never partial).
- **Out of scope:** writing / running / auditing the tests themselves (`e2e-test-automation`, `test-tier-*`, `test-cycle-*`); driving the release (`release-*`); deriving *new* test cases (that stays `test-cycle-case-determination`). This capability only *selects* over existing cases at release level.
- **Origin:** issue #376 (author `nolte`, repo OWNER — trusted). Classification feature-request (secondary spec-change); route pipeline (new roadmap item R-11).

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `6` (3 turns × 2 tightly-coupled decision questions; spec defaults, unchanged)
- `U_gate = min_d c_d` over required dimensions = **0.85**
- Termination: `saturation` (all required dimensions ≥ `τ_high` via authoritative operator choices; remaining gaps are non-load-bearing spec-authorship details recorded as assumptions)

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.90 | specification | Operator choice: traceability-inverse attribution + minimal scope derivation + auditable report |
| `non_functional` | yes | 0.88 | specification | Issue guarantee triad (zielgenau/zeitnah/vollständig-im-Bereich) restated and unchallenged |
| `constraints` | yes | 0.85 | specification | Operator choice: home = nolte-engineering; build on anchor specs, no duplication |
| `domain_objects` | yes | 0.85 | interpretation | Derived from issue + answers; teach-back on change-set / area / TC-ID / verifying-test vocabulary |
| `actors` | yes | 0.85 | interpretation | Operator choice: standalone skill invoked before rollout + read-only scanner agent |
| `acceptance_criteria` | yes | 0.88 | specification | Operator choice: "every requirement has a green test at the appropriate tier; gap = blocker/risk" |
| `edge_cases` | yes | 0.85 | specification | Operator choice: non-attributable change → worst-case full-area regression + residual-risk note |
| `scope_boundaries` | yes | 0.88 | specification | Operator choice: release-level aggregate, selects existing TC-IDs, no case derivation |

## Requirements

- **R1** — WHEN a release change-set is analysed, the system SHALL attribute each change to its impacted topic area(s) primarily via the existing test↔requirement traceability (change → requirement / feature-ID / TC-ID → verifying tests).
  - _dimension_: `functional` · _status_: `confirmed` · _source_: "Traceability-invers (Requirement/TC-ID)"
- **R2** — WHEN a change cannot be mechanically attributed to a topic area, the system SHALL fall back to the full regression set of all plausibly-impacted area(s) and emit a residual-risk note, rather than guess a narrower scope.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: "Worst-case: volle Bereichs-Regression"
- **R3** — WHEN the impacted topic areas are known, the system SHALL derive the minimal set of tiers/tests (E2E emphasised for user-journey coverage) that fully covers those areas' functional requirements.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: issue "Derive the required regression scope"
- **R4** — An impacted topic area SHALL be considered "fully covered" only WHEN every functional requirement of that area has an existing, green verifying test at the appropriate tier; WHEN a required verifying test is missing, the system SHALL report the area as not fully covered and surface the coverage gap as a release blocker / risk.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: "Jedes Requirement hat grünen Test @ passender Tier"
- **R5** — WHEN the scope is determined, the system SHALL produce an auditable report listing in-scope areas, selected tests, deliberately-excluded areas with rationale, and a residual-risk note for anything not mechanically attributable.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: issue "Report the scope … auditable rollout decision"
- **R6** — The determined scope SHALL satisfy the guarantee triad: zielgenau (only impacted areas gate the release), zeitnah (runnable fast enough not to block rollout), and vollständig-im-Bereich (complete functional-requirement regression coverage within each impacted area, never partial).
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: issue "Goal / guarantee"
- **R7** — The capability SHALL select over already-existing TC-IDs / tests aggregated across the whole release range and SHALL NOT derive new test cases; case derivation remains `test-cycle-case-determination` (per-cycle), of which this capability is the release-level aggregate analogue.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: "Release-Level-Aggregat, selektiert bestehende TC-IDs"
- **R8** — The capability SHALL be homed in the `nolte-engineering` plugin and delivered as a new spec (`release-regression-scope`) operationalised into a standalone skill (scope determination) plus a read-only scanner agent (change→area attribution), mirroring `e2e-test-automation` and the `test-cycle-*` family, building on the existing anchor specs without duplicating them.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: "nolte-engineering" + "Standalone-Skill + read-only Scanner-Agent"
- **R9** — The primary actor is the release operator / maintainer invoking the standalone skill before rollout; the change→area scanner agent SHALL be read-only.
  - _dimension_: `actors` · _status_: `confirmed` · _source_: "Standalone-Skill + read-only Scanner-Agent"
- **R10** — Writing, running, or auditing the tests themselves and driving the release SHALL remain out of scope, delegated to the existing test and release capabilities.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: issue "don't duplicate" prior-art anchors

### Domain objects

`change-set`, `release range`, `topic area (Themengebiet)`, `functional requirement`, `requirement / feature-ID / TC-ID`, `verifying test`, `tier`, `regression scope`, `coverage gap`, `residual-risk note`, `auditable scope report`.

## Surviving assumptions / open risks

- **A1 (assumed)** — The "release range" is resolved from the last published release to the release-candidate tip (its merged PRs / diff / touched paths). The exact range-resolution mechanism is a spec-authorship detail. _source_: issue "diff of the release range / merged PRs / touched paths".
- **A2 (assumed)** — The inverse index (requirement / TC-ID → verifying tests) is either read from the traceability that `e2e-test-automation` / `test-case-derivation` already mandate, or built by the scanner agent at scan time; which one is a spec-authorship detail.
- **A3 (assumed)** — "Topic area / Themengebiet" granularity maps to the requirement/feature grouping already present under `project/requirements/` + `project/features/`; no new taxonomy artefact is introduced unless the spec finds it necessary.
- **Open risk (non-blocking)** — Whether `release-skill-layer` should later *reference* this as an optional pre-rollout gate. The operator chose the standalone skill+agent form; a release-layer reference is a possible follow-up, not part of this scope.
