# Release Regression Scope

Status: draft
Portfolio-Scope: local

## Context

A full end-to-end regression suite is too slow to run on every release, so running it always blocks a timely rollout. Running an arbitrary subset instead is unsafe: a functional area can silently break. The portfolio already has the building blocks to *write, run, and audit* tests (`spec/project/test-pyramid-foundation/`, the `test-tier-*` family, `spec/project/e2e-test-automation/`, the `test-cycle-*` family) and to *drive a release* (`spec/project/release-skill-layer/`, `release-automation`, `release-artifact`). What's missing is the **selection step** in between: given a release's change-set, decide *which* topic areas (`Themengebiete`) are impacted and therefore *which* regression tests must run before shipping. No more, no less.

This spec governs that release-level selection discipline. It's the release-scoped analogue of `spec/project/test-cycle-case-determination/`, which answers "which cases" for a single test cycle; this spec answers "which regression scope" across a whole release range. It deliberately owns only the *scoping* decision: it consumes the test↔requirement traceability that `e2e-test-automation` and `test-case-derivation` already mandate and selects over the test cases that already exist. It never writes, runs, audits, or derives tests, and it never drives the release.

It's operationalised in the `nolte-engineering` plugin as a standalone skill (scope determination) plus a read-only scanner agent (change→area attribution), mirroring how `e2e-test-automation` and the `test-cycle-*` family pair a governing spec with a generator/reviewer/scanner toolchain. The spec governs the discipline; the skill and agent operationalise it.

Readers: skill/agent authors maintaining this toolchain; release operators and maintainers who must gate a rollout on a trustworthy-but-fast regression subset; reviewers verifying that a selected scope is both targeted and complete within every area it touches.

## Goals

- Derive the impacted topic areas of a release from its actual change-set, mechanically and in an auditable way.
- Select the minimal set of tiers and tests (E2E emphasised for user-journey coverage) that fully covers the functional requirements of every impacted area.
- Guarantee the triad: `zielgenau` (only impacted areas gate the release), `zeitnah` (the selected subset runs fast enough not to block rollout), `vollständig-im-Bereich` (regression coverage of every impacted area's functional requirements is complete, never partial).
- Make the rollout decision auditable: what's in scope, what's deliberately excluded and why, and what residual risk survives.
- Fail safe: when a change can't be attributed, widen to the full area rather than guess a narrower scope.

## Non-Goals

- Writing, running, or auditing the tests themselves, which stays with `e2e-test-automation`, the `test-tier-*` family, and the `test-cycle-*` family.
- Deriving *new* test cases, which stays with `test-cycle-case-determination` (per-cycle) and `test-case-derivation` (abstract cases). This spec only *selects* over cases that already exist.
- Driving the release (publishing, tagging, workflow dispatch), which stays with the `release-*` specs.
- Mandating a specific release-range mechanism or a specific traceability index format; those are operationalisation choices left to the skill and agent (see Open Questions).

## Requirements

Change-set and attribution

- **R1** The capability MUST resolve the release change-set (the set of changes going into the release: the diff of the release range, its merged pull requests, and its touched paths) before any attribution.
- **R2** Each change MUST be attributed to its impacted topic areas primarily by inverting the existing test↔requirement traceability: change → requirement / feature-ID / TC-ID → verifying tests. The attribution MUST lean on the traceability `e2e-test-automation` and `test-case-derivation` already mandate rather than inventing a parallel mapping.
- **R3** When a change can't be mechanically attributed to a topic area, the capability MUST fall back to the full regression set of every plausibly-impacted area and MUST record an auditable residual-risk note. It MUST NOT silently choose a narrower scope.

Scope derivation and completeness

- **R4** From the impacted areas, the capability MUST derive the minimal set of tiers and tests that covers those areas' functional requirements, emphasising E2E for user-journey coverage.
- **R5** An impacted area MUST be treated as *fully covered* only when every functional requirement of that area has an existing, green verifying test at the appropriate tier. Partial coverage of a touched area is never "covered."
- **R6** When a required verifying test is missing for an impacted area, the capability MUST report that area as not fully covered and MUST surface the coverage gap as a release blocker or an explicit risk, rather than treating the area as passing.

Report and guarantees

- **R7** The capability MUST emit an auditable scope report listing the in-scope areas, the selected tests, the deliberately-excluded areas with a rationale for each exclusion, and the residual-risk note for anything not mechanically attributable.
- **R8** The selected scope MUST satisfy the guarantee triad (`zielgenau`, `zeitnah`, `vollständig-im-Bereich`); a scope that gates on an area that isn't impacted, that can't run in time, or that leaves an impacted area partially covered violates this spec.
- **R9** The capability SHOULD produce identical output whichever tooling path is taken (for example whether it reads GitHub data over an MCP server or the `gh` CLI), so a headless or CI run is trustworthy.

Delimitation and operationalisation

- **R10** The capability MUST only *select* over already-existing TC-IDs aggregated across the whole release range; deriving new cases stays `test-cycle-case-determination`.
- **R11** The change→area scanner MUST be read-only; it attributes and reports but writes nothing and runs no tests.
- **R12** The discipline SHOULD be homed in `nolte-engineering` and delivered as a standalone skill plus a read-only scanner agent, building on the anchor specs (`e2e-test-automation`, `test-pyramid-foundation`, `test-tier-*`, `test-cycle-*`, `test-case-derivation`, `release-*`) without duplicating them.
- **R13** `release-skill-layer` MAY reference the capability as an optional pre-rollout gate; the reference is a consumer choice and isn't required by this spec.

## Acceptance Criteria

- [ ] The spec resolves a release change-set (range diff, merged PRs, touched paths) before attributing anything. (R1)
- [ ] Attribution inverts the existing test↔requirement traceability (change → requirement/TC-ID → verifying tests) rather than a parallel mapping. (R2)
- [ ] A non-attributable change widens to full-area regression and records a residual-risk note; it never narrows silently. (R3)
- [ ] The derived scope is the minimal tier/test set covering the impacted areas' functional requirements, with E2E emphasised. (R4)
- [ ] An area counts as fully covered only when every functional requirement has a green verifying test at the appropriate tier. (R5)
- [ ] A missing verifying test surfaces as a coverage-gap blocker/risk, not a silent pass. (R6)
- [ ] The scope report lists in-scope areas, selected tests, deliberately-excluded areas with rationale, and the residual-risk note. (R7)
- [ ] The scope demonstrably satisfies `zielgenau`, `zeitnah`, and `vollständig-im-Bereich`. (R8)
- [ ] The scanner is read-only and the discipline is delimited from case derivation (selects existing TC-IDs only). (R10, R11)
- [ ] The capability is homed in `nolte-engineering` as a skill + read-only scanner agent, citing the anchor specs without duplicating them. (R12)

## Open Questions

- **A1** Release-range resolution: is the range the last published release to the release-candidate tip, its merged PRs, or its touched paths, and how are the three reconciled? Left to the skill/agent operationalisation.
- **A2** Inverse index: is the requirement/TC-ID → verifying-test index read from the traceability `e2e-test-automation` / `test-case-derivation` already mandate, or built by the scanner at scan time? An operationalisation detail.
- **A3** Topic-area granularity: does `Themengebiet` map to the existing requirement/feature grouping under `project/requirements/` and `project/features/`, or does it need its own taxonomy artefact? Prefer reusing the existing grouping unless a gap forces a new one.
- **A4** Whether `release-skill-layer` should adopt the optional reference of R13, and on what trigger. Non-blocking follow-up.
