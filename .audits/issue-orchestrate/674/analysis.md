---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "674"
classification: "feature-request"
secondary-classes: [spec-change]
route: "direct"
status: approved
created: "2026-09-25"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #674 — capability-reach-audit: anchor a probe on the cited section rather than the whole declaration file
- **URL**: <https://github.com/nolte/claude-shared/issues/674>
- **Labels**: none
- **Linked items**: #668 / #673 (merged `66409882`); no PR references #674.
- **Prior art checked**: no open PR; no `project/features/` entry.
- **Trusted author**: `nolte` (repository owner; filed in this session).

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: spec-change (new requirements in `spec/project/capability-reach-audit/`, schema v1.2)
- **Rationale**: new capability (section anchors, re-confirmation, migration) that lowers operator effort; nothing is broken.
- **Asserted cause verified**: the issue asserts no defect cause. Its premise ("an edit elsewhere in a large requirement document stales every probe on it") is measured: replay over `spec/req/REQ-025_Datenschutz-Betroffenenrechte.md` in nolte/kamerplanter (`origin/develop`, 17 edits, 5 probes) gives 85 stale events with file anchors and 11 with section anchors; the file opens with a change-history table that every edit extends.

## Requirements gate

`project/requirements/reach-probe-section-anchor.md` (committed on this branch at `31299b09`), produced by `requirements-elicit`, `U_gate = 0.8 = τ_high`, R1–R10 `confirmed` after teach-back.

## Scope

- **In scope**: R1–R10 of the requirement artifact.
- **Out of scope**: section anchors for non-Markdown declarations; following a renumbered section; running the migration in a consumer repository.

## Route

- **Decision**: direct (operator-confirmed 2026-09-25) — one outcome (lower re-derivation effort), one capability, one PR strand; no roadmap item.

## Work packages

### P1 — Spec: section anchors, re-confirmation, migration

- **Problem statement**: `spec/project/capability-reach-audit/` knows only the content anchor (#673). Add requirements for R1–R8 in the change-detection block and acceptance criteria; mirror in `de.md`; walk restatements.
- **Acceptance criteria**: EN/DE parity; `pre-commit run --files` Passed.
- **Specialist**: skill `nolte-shared:spec`
- **Depends on**: none

### P2 — Schema v1.2 and runner: section locators, per-locator digests, re-confirmation marker, replay

- **Problem statement (hypothesis)**: `schemas/reach-probe-v1.2.schema.yaml` (new file) adds `declaration.sections: [{heading|row, digest}]` and an approval marker distinguishing `derived` from `reconfirmed`; a section-anchored probe carries `derived_from: "sections:<digest over its locator digests>"` so the existing baseline walk (`probe_changes`, `_anchor_key`) keeps working. The runner resolves `heading`/`row` per R2 (ATX headings outside code fences; pipe tables), reports stale per locator (R3), treats an ambiguous locator as not anchorable (R4), keeps #673's anti-laundering proof for section anchors and re-confirmations (R7: a re-confirmation may change only the anchor and the approval), and reports re-confirmed probes distinctly (R6). A replay command (R10) counts file-anchor vs section-anchor stale events over a declaration's history.
- **Acceptance criteria**: red-first tests for every R; laundering tests from #673 extended to sections and re-confirmation; replay reproduces 85 → 11 on a fixture built from the measured shape; v1.0/v1.1 unchanged; `pytest tests -q` green.
- **Specialist**: `nolte-engineering:fullstack-developer`
- **Depends on**: none

### P3 — Skill and scanner: `reconfirm` and `migrate` operations, locator proposals

- **Problem statement**: the skill gains `reconfirm` (R5: diff per probe, approval per probe, marker) and `migrate` (R8: propose locators for every Markdown-anchored probe, approve per probe); the scanner proposes `declaration.sections` for Markdown declarations (R1, R4); references document states and reasons. SKILL.md body is below the warning band today; new operations go into `references/` where they would push it over.
- **Acceptance criteria**: `validate_skills.py plugins/nolte-engineering/` no Critical, no budget finding; examples validate against v1.2.
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P2 (field names, reason strings)

### P4 — Replay measurement for the PR (R10)

- Run P2's replay against nolte/kamerplanter `origin/develop` REQ-025 and record the output in the PR.
- **Specialist**: orchestrator (measurement)
- **Depends on**: P2

## Dependency ordering

P1 ; P2 → P3 ; P2 → P4.

## Risks

- **Size**: the largest change of this capability since #663; the independent verification of #673 found laundering paths after a green gate — plan the same pass here.
- **Markdown edge cases** (setext headings, fenced code, tables without leading pipe) must fail as not-resolvable, never cut a wrong section.

## Open questions

none

## Dispatch log
2026-09-25 P1 via skill `nolte-shared:spec` (operation 2, update) — two requirements after en.md:78/de.md:78 (SHOULD section anchor with the measured 85→11 replay; MUST re-confirmation with diff, per-probe approval, report mark, weakening on other changes, same move proof, one-time migration) and one AC after :141; parity EN/DE 59 bullets, 14 AC, 16 headings; vale --output=line on en.md empty.
2026-09-25 P2 dispatched to `nolte-engineering:fullstack-developer` — schema v1.2 (`declaration.sections` with heading/row + sha256 digest, `derived_from: sections:<sha256>`, `approval.mode`), runner section resolution, stale per locator, re-confirmation as continuation of the recording derivation, migration, `reach_replay.py`. Red run 48 failed / 14 passed; after: 669 passed, 2 skipped; `test_668_*` unchanged green; mutation probes (previous-section proof, re-confirmation check, baseline digest check) each turn tests red. Deviations recorded with tests: re-confirmation compared against the recording derivation (else an intermediate weakening could be adopted); re-confirmation cannot change locators (migration records as derived); ambiguity at HEAD is stale, at re-derivation weakened; section→blob relabel supported.
