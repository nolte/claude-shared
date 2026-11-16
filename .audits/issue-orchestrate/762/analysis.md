---
artifact-type: issue-orchestration-analysis
repo: nolte/claude-shared
issue: "762"
classification: spec-change
secondary-classes: [feature-request]
route: direct
status: approved
created: 2026-11-16
---

# Issue Orchestration — Pre-analysis (#762)

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #762 — settle three verdict ambiguities in the v1.2 update-security scenarios
- **Labels**: spec, nolte-linux
- **Linked items**: #754 / PR #761 (merged 4170636e), #728
- **Prior art checked**: no comments, no linked PR (`gh issue view 762`, `gh pr list --search 762`)
- **Requirement gate**: `project/requirements/nolte-linux-plugin.md` `U_gate = 0.80 = τ_high` — met

## Maintainer decision (operator, 2026-11-16)

1. **`fail` wins** over "update source not contacted" when a report fails an assertion: a wrong version or an unhealthy report is evidence on its own.
2. **Positive control at scenario level only**: a signature-rejection variant `pass` means "refusal observed"; the control decides the scenario verdict.
3. **Previous-version artifact strictly older than N**: N itself or an equal version makes the downgrade scenario `not-run` with a reason, since installation can't be told from refusal.

## Classification

- **Primary class**: spec-change
- **Secondary**: feature-request (runner follows decision 3)
- **Asserted cause verified**: confirmed on develop 4170636e — (1) `boot_verify.py:1337–1366` returns `fail` on a failed assertion before the `delivered` check; (2) control only at `:1395` (downgrade) and `:1471` (scenario), variant records keep `pass`; (3) the precondition rejects only `compare_versions(prev, N) > 0`, so equality passes; §H `en.md:95` allows "the artifact under test itself".
- **Additional drift found**: §I downgrade step 4 (`en.md:132`) says "recorded no request"; since #761 the runner counts only a fully delivered payload (`_observe_refusal`, `server.delivered`).

## Scope

- **In scope**: spec `image-boot-verification` §H inputs, §H verdict rules (line ~108), §I positive control, downgrade steps 3–4, signature-rejection aggregation (EN+DE, acceptance criteria); schema v1.2 `previous_artifact` description (`schemas/image-boot-protocol-v1.2.schema.yaml:179`); runner precondition for decision 3; CLI help (`boot_verify.py:1823`); `runner.md:43`; `image-boot-verify/SKILL.md:46`; tests pinning all three rules.
- **Out of scope**: real boot (#728); other residual LOW findings from #761.

## Route

- **Decision**: direct — one outcome (one consistent verdict rule set), one PR strand.

## Work packages

### P1 — Spec: write the three rules and the delivery wording

- **Acceptance criteria**: §I/§H state (1) fail precedence, (2) control scope, (3) strictly older previous artifact with the `not-run` reason; step 4 speaks of delivery, not request; matching acceptance criteria; EN/DE parity; no remaining "N itself" in spec (`git grep`).
- **Touched files**: `spec/project/image-boot-verification/{en,de}.md`
- **Specialist**: `nolte-shared:spec` (skill, inline)
- **Depends on**: none

### P2 — Runner, schema text, docs, tests

- **Acceptance criteria**: previous artifact with version equal to N (compare_versions == 0) or digest equal to the artifact under test → downgrade `not-run` with a clear reason, no boot; schema description, CLI help, `runner.md`, `SKILL.md` no longer offer N itself; deterministic tests: equal version → not-run; same file → not-run; fail + undelivered → `fail` (pins decision 1); variant `pass` with scenario `not-run` without control (pins decision 2); mutation probe on the new precondition; `tests/test_boot_verify_runner.py` + `tests/test_validate_boot_protocol.py` green; assertions on timeouts stay factor-aware.
- **Touched files**: `plugins/nolte-linux/skills/image-boot-verify/scripts/boot_verify.py`, `.../references/runner.md`, `.../SKILL.md`, `schemas/image-boot-protocol-v1.2.schema.yaml`, `tests/test_boot_verify_runner.py`
- **Specialist**: no matching specialised agent loaded (nolte-engineering not in this session) — generalist remediation, then a fresh read-only review
- **Depends on**: P1

## Dependency ordering

P1 → P2

## Risks

- Schema change is description-only (no structural change) — verify the schema still validates the existing examples (`tests/test_validate_boot_protocol.py`).
- Behaviour change for operators who passed N itself: downgrade becomes `not-run`, so a field-updated run exits `2` until a real N−1 exists. State in the PR.

## Open questions

none

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|
| §I step 4 says "request", runner counts delivery | acquire measurement | fix directly in P1 | `en.md:132` vs `_observe_refusal` | — |

## Dispatch log
